# $language = "python"
# $interface = "1.0"
"""
Created on 5-23-24 by Mitch Kelley

juniper_reset.py

This script was created to automate the process of wiping specific Juniper switches,

allowing multiple units to run concurrent.

"""
# CRT Variables
objTab = crt.GetScriptTab()
objTab.Screen.Synchronous = True
objTab.Screen.IgnoreEscape = True
end_line = chr(13)
confirmation = 'y' + end_line

# Set variables for 'safe mode'
krnlPrompt = "/kernel"
ldPrompt = "loader>"
binPrompt = "/bin/sh"
error = "continue, shell, abort, retry, or reboot ?"
pwPrompts = ["password:", "New password:", "Retype new password:", "Password:"]
prompts = ["root#", "root>", "root@", "root@DS03-UDC-EX4550>"]
lgnPrompt = "login:"

# Sends 2 "spaces" to interrupt normal boot
objTab.Screen.WaitForString(krnlPrompt)
objTab.Screen.Send(" ")
objTab.Screen.Send(" ")

# Waits for loader prompt
objTab.Screen.WaitForString(ldPrompt)
objTab.Screen.Send("boot -s" + end_line)

# Looks for the /bin prompt and sends the recovery command
objTab.Screen.WaitForString(binPrompt)
objTab.Screen.Send("recovery" + end_line)

# Loop for error handling.
while True:
    screen_output = objTab.Screen.ReadString(error, 30)
    if screen_output:
        objTab.Screen.Send("con" + end_line)
    else:
        break

# Waits for root prompt then sends and confirms the zeroize command
objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("request system zeroize" + end_line)
objTab.Screen.Send(confirmation)

# Wait for the login prompt and logs into switch
objTab.Screen.WaitForString(lgnPrompt)
objTab.Screen.Send("root" + end_line)

objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("cli" + end_line)

objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("edit" + end_line)

# looks for the root with # prompt and sends the reset password command
objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("set system root-authentication plain-text-password" + end_line)

# Sets the password to juniper1
objTab.Screen.WaitForStrings(pwPrompts)
objTab.Screen.Send("juniper1" + end_line)

# Confirm password
objTab.Screen.WaitForStrings(pwPrompts)
objTab.Screen.Send("juniper1" + end_line)

# auto-image disable
objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("delete chassis auto-image-upgrade" + end_line)

# sets device to VC-M"
objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("delete virtual-chassis" + end_line)

# sends the commit command to the switch to save the changes
objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("commit" + end_line)

# sends 2 exit commands to the switch
objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("exit" + end_line)
objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("exit" + end_line)

# Reboot system
objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("reboot" + end_line)

# Wait for the login prompt
objTab.Screen.WaitForString(lgnPrompt)
objTab.Screen.Send("root" + end_line)

# Define list and strings
wait_strings = pwPrompts + prompts
output = objTab.Screen.WaitForStrings(wait_strings)

# Handle pw master error
if output <= 4:
    objTab.Screen.Send("juniper1" + end_line)
    objTab.Screen.WaitForStrings(prompts)
    objTab.Screen.Send("cli" + end_line)
elif output == 7:
    objTab.Screen.Send("LOGIC ERROR")

# loop to handle errors for hardware search
objTab.Screen.Send("show chassis hardware" + end_line)
# Define and update strings
erPrompt = objTab.Screen.ReadString("root>")
while True:
    if "error:" in erPrompt:
        objTab.Screen.Send("show chassis hardware" + end_line)
    else:

        # If inventory found break loop
        if "Hardware inventory:" in erPrompt:
            break
# Send message to screen that format is finished.
# format_complete = objTab.Screen.ReadString(rebootPrompt)
# if format_complete:
# message = "Sanitation Complete"
# crt.Dialog.MessageBox(message)
