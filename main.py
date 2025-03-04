from jnius import autoclass, PythonJavaClass, java_method
from kivy.app import App

# Accessing Android classes using Pyjnius
BroadcastReceiver = autoclass('android.content.BroadcastReceiver')
SmsMessage = autoclass('android.telephony.SmsMessage')
SmsManager = autoclass('android.telephony.SmsManager')

# Custom BroadcastReceiver for listening to SMS
class SmsReceiver(PythonJavaClass):
    __javainterfaces__ = ['android/content/BroadcastReceiver']

    @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
    def onReceive(self, context, intent):
        # Retrieve SMS from the intent
        bundle = intent.getExtras()
        pdus = bundle.get("pdus")
        if pdus:
            for pdu in pdus:
                sms = SmsMessage.createFromPdu(pdu)
                sender = sms.getOriginatingAddress()
                message = sms.getMessageBody()

                # If the message contains the 'CONTACT' command
                if message.startswith("CONTACT"):
                    contact_name = message.split(" ")[1]
                    contact_number = self.get_contact_number(context, contact_name)
                    self.send_sms(sender, contact_number)

    def get_contact_number(self, context, contact_name):
        # Query Android contacts and return the phone number
        ContentResolver = autoclass('android.content.ContentResolver')
        ContactsContract = autoclass('android.provider.ContactsContract')
        content_resolver = context.getContentResolver()

        # Build query
        uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI
        selection = "{} = ?".format(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
        cursor = content_resolver.query(uri, None, selection, [contact_name], None)

        if cursor.moveToFirst():
            number_index = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
            contact_number = cursor.getString(number_index)
            cursor.close()
            return contact_number
        else:
            return "Contact Not Found"

    def send_sms(self, phone_number, message):
        # Use SmsManager to send a message
        sms_manager = SmsManager.getDefault()
        sms_manager.sendTextMessage(phone_number, None, message, None, None)

# Main App
class MyHelperApp(App):
    def build(self):
        return

if __name__ == '__main__':
    MyHelperApp().run()
