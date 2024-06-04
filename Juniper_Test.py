# $language = "python"
# $interface = "1.0"

# CRT Variables
objTab = crt.GetScriptTab()
objTab.Screen.Synchronous = True
objTab.Screen.IgnoreEscape = True
end_line = chr(13)
confirmation = 'y' + end_line

# Variables for EX4550
krnlPrompt = "/kernel"
ldPrompt = "loader>"
binPrompt = "/bin/sh"
error = "continue, shell, abort, retry, or reboot ?"
pwPrompts = ["password:", "New password:", "Retype new password:", "Password:"]
prompts = ["root#", "root>", "root@", "root@:RE:0%"]
lgnPrompt = "login:"

# # Sends 2 "spaces" to interrupt normal boot
# objTab.Screen.WaitForString(krnlPrompt)
# objTab.Screen.Send(" ")
# objTab.Screen.Send(" ")
#
# # Wait for loader prompt and boot into safemode
# objTab.Screen.WaitForString(ldPrompt)
# objTab.Screen.Send("boot -s" + end_line)
#
# # Looks for /bin prompt and send recovery command
# objTab.Screen.WaitForString(binPrompt)
# objTab.Screen.Send("recovery" + end_line)
#
# # Loop for error handling.
# while True:
#     screen_output = objTab.Screen.ReadString(error, 30)
#     if screen_output:
#         objTab.Screen.Send("continue" + end_line)
#     else:
#         break
#
# # Start system zeroize
# objTab.Screen.WaitForStrings(prompts)
# objTab.Screen.Send("request system zeroize" + end_line)
# objTab.Screen.Send(confirmation)

# List of commands to finish wiping unit
strings = [
    "cli",
    "edit",
    "set system root-authentication plain-text-password",
    "delete virtual-chassis",
    "delete chassis auto-image-upgrade",
    "commit",
    "exit"]

# Iterate over list to confirm password.
# for Index, string in enumerate(strings):
#     if Index == 3:
#         objTab.Screen.ReadString("New password:")
#         objTab.Screen.Send("juniper1" + end_line)
#     if Index == 4:
#         objTab.Screen.WaitForString("Retype new password:")
#         objTab.Screen.Send("juniper1" + end_line)
#     if Index <= 2 or Index >= 5:
#         objTab.Screen.Send(string + end_line)

for string in strings:
    if string == strings[2]:
        pwset = "set system root-authentication plain-text-password"
        pw_string = objTab.Screen.ReadString("root#")
        objTab.Screen.ReadString("root#")
        if pwset in pw_string:
            objTab.Screen.Send("juniper1" + end_line)
            objTab.Screen.Send("juniper1" + end_line)
        # objTab.Screen.WaitForString("Retype new password:")
        # objTab.Screen.Send("juniper1" + end_line)
    elif string <= strings[1] or string >= strings[3]:
        objTab.Screen.WaitForStrings(prompts)
        objTab.Screen.Send(string + end_line)


# View PID/Hardware status
objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("show chassis hardware" + end_line)
