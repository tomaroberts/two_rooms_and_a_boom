# Had to run following line in python terminal venv to get email to work:
# pip install --upgrade certifi
#
# Then source bin/activate to activate venv
#
# Then python3.7 two_rooms_and_a_boom.py to run

import csv
import random
import smtplib
import ssl
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#--- Setup
# EDIT THIS BLOCK BEFORE RUNNING
dir_path = r'/set/path/to/dir/ending/in/two_rooms_and_a_boom'
email_address = 'email_address@gmail.com'

# Gmail changed password security as of May 2022. Now need to set up App Passwords
# See here: https://support.google.com/accounts/answer/185833?hl=en
# Basically, ensure 2FA configured, then goto 2-Step Verification section and select App Passwords
password = '2fa_password'
port = 465  # For SSL
#--- end Setup


# List of Players
email_list = []
with open(os.path.join(dir_path, 'emails.csv'), newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in reader:
        email_list.append(row[0])

N_players = len(email_list)

# Print To Screen
print("\n\n---------------------------------------------------------\n")
print(f"Hi! Welcome to Two Rooms and  Boom!\n")
print(f"You're playing with the following {N_players} players:\n")
for players in email_list:
    print(players)


# Define Game
mandatory_special_roles = ['President (Blue)', 'Bomber (Red)']

optional_special_roles = [['Hot Potato'],                                   # 0
                          ['Zombie'],                                       # 1
                          ['Security (Blue)', 'Security (Red)'],            # 2
                          ['Doctor (Blue)', 'Engineer (Red)'],              # 3
                          ['Bouncer (Blue)', 'Bouncer (Red)'],              # 4
                          ['Tuesday Knight (Blue)', 'Dr BOOOOOOM (Red)']]   # 5

# Remember to use python indexing (i.e starting from 0)
# example: for two Hot Potatoes chosen_optional_special_roles = [0,0]
chosen_optional_special_roles = [1,3]

# Add chosen roles to utilised roles
utilised_special_roles = mandatory_special_roles
for num in chosen_optional_special_roles:
    for sublist in optional_special_roles[num]:
        utilised_special_roles.append(sublist)

# Figure out how many spots are left in the game
N_special_roles = len(utilised_special_roles)
N_standard_roles_ideal = N_players - N_special_roles
if N_standard_roles_ideal < 0:
    raise Exception("Too few players!")

# Figure out how to assign them between Red and Blue
if (N_standard_roles_ideal % 2) == 0:                       # Even number of standard plays for each team
    N_standard_red = N_standard_roles_ideal / 2
    N_standard_blue = N_standard_red
else:                                                       # But if not...
    if random.randint(0, 2) == 0:                                 # Flip a coin - if heads, Red get one more player
        N_standard_red = (N_standard_roles_ideal + 1) / 2
        N_standard_blue = (N_standard_roles_ideal - 1) / 2
    else:                                                        # Flip a coin - if tails, Blue get one more player
        N_standard_red = (N_standard_roles_ideal - 1) / 2
        N_standard_blue = (N_standard_roles_ideal + 1) / 2

# Fill the rest of the game slots
roles = utilised_special_roles
for i in range(int(N_standard_blue)):
    roles.append('Standard (Blue)')
for i in range(int(N_standard_red)):
    roles.append('Standard (Red)')

if len(roles) != len(email_list):
    raise Exception("Number of roles assigned do not match number of players!")

print(f"\nYou're playing with the following EXCITING roles:\n")
for i in utilised_special_roles:
    print(i)

# Now randomly shuffle roles
random.shuffle(roles)

# Create a secure SSL context
context = ssl.create_default_context()

# Info for message
now = datetime.now()
now_str = now.strftime("%Y/%m/%d %H:%M")
now_str_debug = now.strftime("%Y%m%d_%H%M")

for i in range(N_players):

    message = MIMEMultipart("alternative")
    message["Subject"] = f"{roles[i]} - {now_str}"
    message["From"] = email_address
    message["To"] = email_list[i]

    # Create the plain-text and HTML version of your message
    text = f"""You've been assigned the role of {roles[i]}!"""
    html = f"""\
    <html>
      <body>
        You've been assigned the role of {roles[i]}!
        </p>
      </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email_address, password)
        server.sendmail(email_address, email_list[i], message.as_string())

# Debug Output
with open(os.path.join(dir_path, f'debug_{now_str_debug}.csv'), 'w', newline='') as file:
    writer = csv.writer(file)
    for i in range(N_players):
        writer.writerow([email_list[i], roles[i]])

# Final comments
print(f"\nEmails sent - have a good game!\n")
print("---------------------------------------------------------")
