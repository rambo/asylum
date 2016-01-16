import environ
import logging
import datetime, calendar
from django.utils import timezone
from django.core.mail import EmailMessage
from members.handlers import BaseApplicationHandler, BaseMemberHandler
from creditor.handlers import BaseTransactionHandler, BaseRecurringTransactionsHandler
from creditor.models import Transaction, TransactionTag
from django.utils.translation import ugettext_lazy as _
from examples.utils import get_holvi_singleton

logger = logging.getLogger('hhlcallback.handlers')
env = environ.Env()

class ApplicationHandler(BaseApplicationHandler):
    def on_approved(self, application, member):
        # Welcome-email
        rest_of_year_free = False
        fee_msg_fi = "Jäsenmaksusta tulee sinulle erillinen viesti."
        fee_msg_en = "You will receive a separate message about membership fee."
        # If application was received in Q4, rest of this year is free
        if application.received.month >= 10:
            rest_of_year_free = True
            fee_msg_fi = "Vuoden %s jäsenmaksua ei peritä." % application.received.year
            fee_msg_en = "Membership fee for year %s has been waived." % application.received.year
        mail = EmailMessage()
        mail.to = [ member.email, ]
        mail.from_email = "hallitus@helsinki.hacklab.fi"
        mail.subject = "Helsinki Hacklabin jäsenhakemus hyväksytty! | Your membership application has been approved!"
        mail.body = """Tervetuloa Helsinki Hacklabin jäseneksi!

Jäsenenä olet tervetullut kaikkiin Helsinki Hacklabin tilaisuuksiin, kuten tiistaisiin jäseniltoihin, torstaisiin kurssipäiviin, sekä muihin järjestettäviin tapahtumiin.

Sähköisesti hacklabilaisten kanssa voi keskustella Suomen hacklabien foorumilla (https://discourse.hacklab.fi/), sekä IRC kanavallamme #helsinkihacklab Freenode-verkossa.

{fee_msg_fi}

Jos sinulla on jäsenyyteen tai tähän viestiin liittyviä kysymyksiä, voit lähettää ne Helsinki Hacklabin hallitukselle vastaamalla tähän viestiin tai lähettämällä viestin osoitteeseen hallitus@helsinki.hacklab.fi

----

Helsinki Hacklab welcomes you as a member!

As a member you are most welcome to attend all events organised by Helsinki Hacklab. These include the weekly member gathering every Tuesday, our courses and workshops held on Thurdays and other events we might come up with.

Electronic communication between our members is handled forum of finnish hacklabs (https://discourse.hacklab.fi/) and on our IRC channel #helsinkihacklab @ Freenode.

{fee_msg_en}

For questions regarding your membership or this message, please contact the board of Helsinki Hacklab at hallitus@helsinki.hacklab.fi or simply reply to this message.

""".format(fee_msg_fi=fee_msg_fi, fee_msg_en=fee_msg_en)
        mail.send()

        # Subscribe to mailing list
        mailman_subscribe = env('HHL_MAILMAN_SUBSCRIBE', default=None)
        if mailman_subscribe:
            mail = EmailMessage()
            mail.from_email = member.email
            mail.to = [ mailman_subscribe, ]
            mail.subject = 'subscribe'
            mail.body = 'subscribe'
            mail.send()

        # Auto-add the membership fee as recurring transaction
        membership_fee = env.float('HHL_MEMBERSHIP_FEE', default=None)
        membership_tag = 1
        if membership_fee and membership_tag:
            from creditor.models import RecurringTransaction, TransactionTag
            rt = RecurringTransaction()
            rt.tag = TransactionTag.objects.get(pk=membership_tag)
            rt.owner = member
            rt.amount = -membership_fee
            rt.rtype = RecurringTransaction.YEARLY
            # If application was received in Q4 set the recurringtransaction to start from next year
            if rest_of_year_free:
                rt.start = datetime.date(year=application.received.year+1, month=1, day=1)
            rt.save()
            rt.conditional_add_transaction()



class RecurringTransactionsHolviHandler(BaseRecurringTransactionsHandler):
    def on_creating(self, rt, t, *args, **kwargs):
        # Only negative amounts go to invoices
        if t.amount >= 0.0:
            return True
        HOLVI_CNC = get_holvi_singleton()
        if not HOLVI_CNC:
            return True

        import holviapi
        invoice_api = holviapi.InvoiceAPI(HOLVI_CNC)
        invoice = holviapi.Invoice(invoice_api)
        invoice.receiver = holviapi.contacts.InvoiceContact(**{
            'email': t.owner.email,
            'name': t.owner.name,
        })
        invoice.items.append(holviapi.InvoiceItem(invoice))
        if t.stamp:
            year = t.stamp.year
        else:
            year = datetime.datetime.now().year
        invoice.items[0].description = "%s %s" % (t.tag.label, year)
        invoice.items[0].net = -t.amount # Negative amount transaction -> positive amount invoice
        invoice.subject = "%s / %s" % (invoice.items[0].description, invoice.receiver.name)
        invoice = invoice.save()
        invoice.send()
        t.reference = invoice.rf_reference
        return True
