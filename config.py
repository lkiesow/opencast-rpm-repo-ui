# -*- coding: utf-8 -*-
database='sqlite:///user.db'

# LOGIN

sessionkey = 'bdkfHvkVt(r8%ZGIUZGTRHg'

# EMAIL TO USER */

repourl      = "http://pkg.opencast.org/"
mailsender   = "no-reply@uni-osnabrueck.de"
mailtopic    = "Registration: Opencast Package Repository"
mailtext     = '''Hello %(firstname)s %(lastname)s,
Welcome to the Opencast Package Repository.
Here are your credentials for the repo:

    Username: %(username)s
    Password: %(password)s

For more information, please visit
 ''' + repourl

# EMAIL TO ADMIN */

adminurl          = repourl + "admin"
adminmailadress   = ['lkiesow@uos.de', 'rrolf@uos.de']
adminmailadress   = ['lkiesow@uos.de']
adminmailtopic    = "%(username)s registered on Opencast Package Repository"
adminmailtext     = '''Hello Admin,
%(username)s (%(firstname)s %(lastname)s) signed-up for the Opencast RPM Repo.

Visit ''' + adminurl + ''' to activate his account.'''

# EMAIL FORGOT PASSWORD */

mailsender = 'no-reply@virtuos.uos.de'
forgotmailtopic  = 'Your password for Opencast Repository'
forgotmailtext   = '''Hello,
your login for the Opencast RPM Repository:
'''

# TEXT SUCCESSFULL/ERROR REGESTRATION PAGE */

successtext     = '''Thank you for signing up. Your request will be reviewed
                and you will get an email with your login credentials once your
                request was approved.'''
userexistserror = ('Sign-up failed', '''We are sorry, but a user with this
		username already exists. Please choose another username.''', 'Go back')
emailerror = ('Sign-up failed', '''You are required to use a valid email
		address for registration.''', 'Go back')
captchaerror    = ('Sign-up failed', '''There was an error during the sign up
		process. The equation was not solved correctly. Please try again.''',
		'Go back')
termsofuseuerror = ('Sign-up failed', '''There was an error during the sign up
		process. The terms of use have to be accepted. Please try again.''',
		'Go back')
dberror         = ('Database error', '''An error occurred. The connection to
		the database could not be established. This should not have happened.
		Please report this to lkiesow@uos.de and try again later.''', 'Go back')
loginerror      = ('Log-in failed', '''The log-in failed. Please verify that
		you used the correct username and password and try again.''', 'Go back')
forgotmailerror = ('Password recovery failed', '''There is no active user with
		the given mail address. Please make sure you entered the address
		correctly.''', 'Go back')
forgotsuccess = ('Success', '''A mail containing your login
		credentials has been sent to you.''', '')


# TEXT SIGNUP INFO TEXT */

signupinfotext = "With signing up you will get free access to Matterhorn Repo for CentOS and Fedora."

# TEXT FORGOTTEN PASSWORD SENT */

passwordsenttext = "We sent a mail with your password to you."

#TEXT DELETE MAIL
delete_reasons = [
        'Your request could not be accepted.',
        'Access for non-commercial organizations only.',
        'Invalid or incomplete data.',
        'Duplicated account'
        ]
