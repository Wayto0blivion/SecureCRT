# $language = "python"
# $interface = "1.0"
"""
Created on 5-23-24 by Mitch Kelley

juniper_reset.py

This script was created to automate the process of wiping a sub-set of Juniper units.

Allowing multiple units to run concurrent.

"""
# CRT Variables
objTab = crt.GetScriptTab()
objTab.Screen.Synchronous = True
objTab.Screen.IgnoreEscape = True
end_line = chr(13)
confirmation = 'y' + end_line

# Starts the infinite Loop for the script
mode = 2

while mode == 0:
    # Set variables for 'safe mode'
    krnlPrompt = "/kernel"
    ldPrompt = "loader>"
    binPrompt = "/bin/sh"
    error = "continue, shell, abort, retry, or reboot ?"
    rtPrompt = "root>"
    conf = "#"
    pwPrompts = ["password:", "New password:", "Retype new password:"]
    rbPrompt = "Reboot the system?"
    prompts = ["root#", "root>", "root@", "root@DS03-UDC-EX4550>"]
    
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

    # Waits for the root prompt to pop up and sends the configure command
    objTab.Screen.WaitForStrings(prompts)
    objTab.Screen.Send("configure" + end_line)

    # looks for the root with # prompt and sends the reset password command
    objTab.Screen.WaitForStrings(prompts)
    objTab.Screen.Send("set system root-authentication plain-text-password" + end_line)

    # Sets the password to juniper1
    objTab.Screen.WaitForStrings(pwPrompts)
    objTab.Screen.Send("juniper1" + end_line)

    # sets the password to juniper1 again for the password confirmation prompt
    objTab.Screen.WaitForStrings(pwPrompts)
    objTab.Screen.Send("juniper1" + end_line)

    # sets device to VC-M"
    objTab.Screen.WaitForStrings(prompts)
    objTab.Screen.Send("delete virtual-chassis" + end_line)

    # sends the commit command to the switch to save the changes
    objTab.Screen.WaitForStrings(prompts)
    objTab.Screen.Send("commit" + end_line)

    # sends 2 exit commands to the switch
    objTab.Screen.WaitForStrings(prompts)
    objTab.Screen.Send("exit" + end_line)
    objTab.Screen.Send("exit" + end_line)

    # looks for the y/n prompt and reboots
    objTab.Screen.WaitForString(rbPrompt)
    objTab.Screen.Send(confirmation)

    # Sets the mode to 1 to stop previous loop, so you can enter regular boot
    mode = 1
# starts another loop while mode is 1
while mode == 1:
    # sets the variables for regular boot
    lgnPrompt = "login:"
    pwPrompts = ["password:", "New password:", "Retype new password:", "Password:"]
    rebootPrompt = "Rebooting..."
    resetPrompt = "FLASH:"
    krnlPrompt = "/kernel"
    ldPrompt = "loader>"
    prompts = ["root#", "root>", "root@", "root@DS03-UDC-EX4550>"]

    # Wait for the login prompt and logs into switch
    objTab.Screen.WaitForString(lgnPrompt)
    objTab.Screen.Send("root" + end_line)
    objTab.Screen.WaitForStrings(pwPrompts)
    objTab.Screen.Send("juniper1" + end_line)

    # looks for the root prompt and puts the switch into cli mode
    objTab.Screen.WaitForStrings(prompts)
    objTab.Screen.Send("cli" + end_line)

    # waits for root prompt then sends and confirms the zeroize command
    objTab.Screen.WaitForStrings(prompts)
    objTab.Screen.Send("request system zeroize" + end_line)
    objTab.Screen.Send(confirmation)
    # Set mode to '2' to complete loop
    mode = 2

while mode == 2:
    # set variables for final boot
    lgnPrompt = "login:"
    pwPrompts = ["password:", "New password:", "Retype new password:", "Password:"]
    prompts = ["root#", "root>", "root@", "root@DS03-UDC-EX4550>"]

    # Wait for the login prompt and logs into switch
    objTab.Screen.WaitForString(lgnPrompt)
    objTab.Screen.Send("root" + end_line)

    # Define list and strings
    wait_strings = pwPrompts + prompts
    output = objTab.Screen.WaitForStrings(wait_strings)
    error = objTab.Screen.ReadString("error:")
    HWinv = objTab.Screen.ReadString("Hardware Inventory:")

    # Handle log-in process
    if output <= 4:
        objTab.Screen.Send("juniper1" + end_line)
    elif output == 7:
        objTab.Screen.Send("cli" + end_line)

        # loop to handle timing with chassis sub-system being "inactive".
        while True:
            if output <= 6:
                objTab.Screen.Send("show chassis hardware" + end_line)
                break
            elif error == 1:
                objTab.Screen.Send(end_line)
            elif HWinv == 1:
                mode = 3
                break
    # Send message to screen that format is finished.
    # format_complete = objTab.Screen.ReadString(rebootPrompt)
    # if format_complete:
    # message = "Sanitation Complete"
    # crt.Dialog.MessageBox(message)
