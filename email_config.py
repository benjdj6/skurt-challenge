sender = "EMAIL_GOES_HERE"
email_pass = "EMAIL_PASSWORD_GOES_HERE"
recipients = ["engineering@skurtapp.com"]

oob_plain_msg = """
Car #{0} is out of bounds. You can view it's last known location at {1}\n 
This is an automated message, please do not reply."""

oob_html_msg = """\
<html>
	<head></head>
	<body>
		<p>Car #{0} is out of bounds.
		You can see it's last known location <a href="{1}">here</a>.</p>
		<p>This is an automated message, please do not reply.</p>
	</body>
</html>
"""
oob_subj = "Out of Bounds Warning: Car #{0} has left area"

err_plain_msg = "Server Response: {0}"

err_subj = "Server Error: Car Location Service Returned Status Code {0}"

tout_subj = "Warning: Server Timeout"

tout_plain_msg = "Car Location Server Timed Out Request"