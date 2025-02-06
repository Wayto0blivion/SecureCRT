# $language = "python"
# $interface = "1.0"
import os


def get_log_path():
    """
    Determine the absolute filepath of the directory where script lives
    :return: Absolute filepath of the log file
    """
    script_directory = os.path.dirname(os.path.abspath(__file__))
    logfile_path = os.path.join(script_directory, "crt_log.txt")
    return logfile_path


def log_message(message):
    """
    Saves debugging logs to a separate text file in the same location.
    :param message: Message to save to log file.
    :return: None
    """
    with open(get_log_path(), "a") as file:
        file.write(message + '\n')


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

# Sends 2 "spaces" to interrupt normal boot
objTab.Screen.WaitForString(krnlPrompt)
objTab.Screen.Send(" ")
objTab.Screen.Send(" ")

# Wait for loader prompt and boot into safemode
objTab.Screen.WaitForString(ldPrompt)
objTab.Screen.Send("boot -s" + end_line)

# Looks for /bin prompt and send recovery command
objTab.Screen.WaitForString(binPrompt)
objTab.Screen.Send("recovery" + end_line)

# Loop for error handling.
while True:
    screen_output = objTab.Screen.ReadString(error, 30)
    if screen_output:
        objTab.Screen.Send("continue" + end_line)
    else:
        break

# Start system zeroize
objTab.Screen.WaitForStrings(prompts)
objTab.Screen.Send("request system zeroize" + end_line)
objTab.Screen.Send(confirmation)
# objTab.Screen.WaitForString(lgnPrompt)

# List of commands to finish wiping unit
strings = [
    "root",
    "cli",
    "edit",
    "set system root-authentication plain-text-password",
    " ",
    "delete virtual-chassis",
    "delete chassis auto-image-upgrade",
    "commit",
    "exit"]

for string in strings:
    if string is "set system root-authentication plain-text-password":
        objTab.Screen.Send("set system root-authentication plain-text-password" + end_line)
        pw = objTab.Screen.WaitForStrings(pwPrompts)
        objTab.Screen.Send("juniper1" + end_line)
        rpw = objTab.Screen.WaitForStrings(pwPrompts)
        objTab.Screen.Send("juniper1" + end_line)
    if string is "root":
        wait = objTab.Screen.WaitForStrings(lgnPrompt)
        objTab.Screen.Send("root" + end_line)

    else:
        objTab.Screen.Send(string + end_line)
        prompt = objTab.Screen.WaitForStrings(prompts)

# View PID/Hardware status
objTab.Screen.Send("show chassis hardware" + end_line)

# =======================================================================================================
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

# for string in strings:
#     log_message("String: {}".format(string))
#     if string is "set system root-authentication plain-text-password":
#         log_message("PWSET")
#         pwset = "set system root-authentication plain-text-password"
#         pw_string = objTab.Screen.ReadString("root#")
#         log_message("pw_string:  {}".format(pw_string))
#         objTab.Screen.ReadString("root#")
#         if pwset in pw_string:
#             log_message("Found pwset in pw_string")
#             objTab.Screen.Send("juniper1" + end_line)
#             objTab.Screen.Send("juniper1" + end_line)
#         # objTab.Screen.WaitForString("Retype new password:")
#         # objTab.Screen.Send("juniper1" + end_line)
#     else:
#         log_message("set system root-authentication plain-text-password")
#         log_message(objTab.Screen.WaitForStrings(prompts))
#         objTab.Screen.Send(string + end_line)

# objTab.Screen.Send("cli" + end_line)
# log_message(str(objTab.Screen.WaitForStrings(prompts)))
# objTab.Screen.Send("edit" + end_line)
# log_message(str(objTab.Screen.WaitForStrings(prompts)))
# objTab.Screen.Send("set system root-authentication plain-text-password" + end_line)
# log_message(str(objTab.Screen.WaitForStrings(pwPrompts)))
# objTab.Screen.Send("juniper1" + end_line)
# log_message(str(objTab.Screen.WaitForStrings(pwPrompts)))
# objTab.Screen.Send("juniper1" + end_line)
# log_message(str(objTab.Screen.WaitForStrings(prompts)))
