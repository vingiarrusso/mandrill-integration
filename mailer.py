import mandrill
import logging

class Mailer(object):
    def __init__(self):
        self.client = mandrill.Mandrill('your client key')
        # In my case, these options rarely change, so I've put them in the class constructor.
        # I find handlebars syntax to be more intuitive and use them in our templates.
        # Check out the Mandrill documentation to see what is supported with Mandrill handlebars.
        self.defaults = dict(
            from_email="my_email@wherever.com",
            from_name="My Name",
            merge_language="handlebars", 
            track_opens=True,
            track_clicks=True)
    
    def make_mail_params(self, **kwargs):
        """
            A simple abstraction to create Mandrill formatted parameter dictionary for sending emails.  Keys currently supported are:
            email, fname, lname, subject, tags, global_merge_vars, images (jpeg), attachments (jpeg).  If more are needed,
            check out the mandrill api for additional things it can accept and add them in here.  Could also be extended to support different
            image/attachment types if needed.  Mandrill expects images and attachments to be base64 encoded.  This implementation assumes you've already
            done that step.
        """
        return {
            "to": [{
                "email": kwargs.get('email'),
                "name": "{} {}".format(kwargs.get('fname', ""), kwargs.get('lname', "")).strip(),
                "type": "to"
            }],
            "subject": kwargs.get('subject'),
            "tags": kwargs.get('tags', []),
            "global_merge_vars": [{"content": value, "name": key} for key, value in kwargs.get('global_merge_vars', {}).iteritems()],
            "images": [{"content": value, "name": key, "type": "image/jpeg"} for key, value in kwargs.get('images', {}).iteritems()],
            "attachments": [{"content": value, "name": key, "type": "image/jpeg"} for key, value in kwargs.get('attachments', {}).iteritems()],
        }
        
    def send(self, params):
        self.defaults.update(params)
        try:
            result = self.client.messages.send(message=self.defaults, async=False, ip_pool="Main Pool")
            # In this implementation, I add additional items into the return result from Mandrill and process them further (such as adding to a db table).  You may not need to, but
            # this is one way to do that.
            result[0].update({
                'sender': self.defaults["from_email"],
                'subject': self.defaults["subject"]
            })
            return result
        except mandrill.Error as e:
            logging.error(str(e))

    def send_template(self, template_name, params):
        self.defaults.update(params)
        try:
            result = self.client.messages.send_template(
                message = self.defaults,
                # All of my usable templates live in Mandrill, so this is just a placeholder.
                template_content =[],
                template_name = template_name,
                async = False,
                ip_pool = "Main Pool"
                )
            # See comment above.
            result[0].update({
                'sender': self.defaults["from_email"],
                'subject': self.defaults["subject"]
            })
            return result
        except mandrill.Error as e:
            logging.error(str(e))


# Example Usage:
mailer = Mailer()
template_name = 'Your Mandrill template name'
mandrill_result = mailer.send_template(template_name, mailer.make_mail_params(
    email = 'recipient email',
    subject = 'Hello from Mandrill',
    tags = [template_name],
    global_merge_vars = {
        'user_id': 42,
        'user_name': 'Francisco Gerardo',
        'user_key': 'f7994kd49as621'
    },
    images = {'image_cid_name': yourImage.encode('base64')},
    attachments = {'attachment_file_name': yourImage.encode('base64')}
))[0] #mandrill returns a list, you'll probably only ever need the first element.
