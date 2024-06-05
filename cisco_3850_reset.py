# $language = "python"
# $interface = "1.0"

"""
Original created on 4-5-2024 by Dustin Beck

Edited for use with C3k series Cisco switches on 6/5/24 by Mitch Kelley

cisco_3850_reset.py

The purpose of this script is to remove files on C3K devices
while leaving (.conf) files intact.

This script is designed to be run once per device, after the MODE button has been pressed
and the first "switch:" prompt appears, where the SWITCH_IGNORE_STARTUP_CFG=1 command is usually passed.
"""


from datetime import datetime
import json
import os


# Create global variables for loading from JSON
variables = {}


# Set CRT variables
objTab = crt.GetScriptTab()
objTab.Screen.Synchronous = True
objTab.Screen.IgnoreEscape = True
end_line = chr(13)
confirmation = 'y' + end_line  # Set a default confirmation variable


def main():
    """
    Main function for erases Cisco devices automatically.
    :return:
    """
    # Get global references to necessary variables, the set them from the json file
    global variables
    variables = load_variable_file()

    # Start the logging process, clearly indicating a new run.
    log_message("\n\n***********************************************************************************")
    log_message("Starting Cisco Deletion Process: " + str(datetime.now()))
    log_message('Log File Directory: ' + get_log_path())

    handle_device()

    log_message('Ending Cisco Deletion Process.')
    log_message("***********************************************************************************\n\n")


# ====================================================================================================================
# ====================================================================================================================

# End of main function

# ====================================================================================================================
# ====================================================================================================================


def load_variable_file():
    """
    Check for the existence of variables.json. If it exists, load it and return the variables.
    If it doesn't exist, create it and load default variables into the file.
    :return: prompt, directory, excluded_directories: Variables to be loaded globally.
    """
    # Get the absolute path to the directory where the script is stored
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Get the absolute filepath for where the variable file will be.
    variables_path = os.path.join(script_directory, "variables.json")

    # Check if the file exists
    if not os.path.exists(variables_path):
        # File doesn't exist, create it with default data
        log_message('load_variable_file: No variable file detected.')
        default_data = {
            "prompt": 'switch',
            "directory": 'flash:',
            "excluded_directories": ['html'],
            "rommon_files": ['vlan.dat', 'multiple-fs', 'config.text'],
            "boot_command": 'boot flash:packages.conf',
            "boot_message": 'Press RETURN to get started!',
            "file_extension": ['.pkg', '.conf']
        }
        # create the file and write the default data to it
        with open(variables_path, 'a') as file:
            json.dump(default_data, file)
        log_message('load_variable_file: Variables file created! {}'.format(variables_path))

    # File definitely exists now, load data into variables
    with open(variables_path, 'r') as file:
        log_message('load_variable_file: Reading variables from file: {}'.format(variables_path))
        data = json.load(file)

        return data


def log_message(message):
    """
    Saves debugging logs to a separate text file in the same location.
    :param message: Message to save to log file.
    :return: None
    """
    with open(get_log_path(), "a") as file:
        file.write(message + '\n')


def display_to_user(message):
    """
    Display a crt.Dialog.MessageBox to user to alert them to a prominent error.
    :param message: String to display to user.
    :return:
    """
    crt.Dialog.MessageBox(message)


def get_log_path():
    """
    Determine the absolute filepath of the directory where script lives
    :return: Absolute filepath of the log file
    """
    script_directory = os.path.dirname(os.path.abspath(__file__))
    logfile_path = os.path.join(script_directory, "3850_log.txt")
    return logfile_path


def ignore_startup():
    """
    Run the 'SWITCH_IGNORE_STARTUP_CFG=1' command and wait for the prompt to appear
    :return:
    """
    objTab.Screen.Send("SWITCH_IGNORE_STARTUP_CFG=1" + end_line)
    objTab.Screen.WaitForStrings([variables['prompt']])
    log_message('Ignore startup: Prompt found!')


def boot_device():
    """
    Handles running the boot command and getting back to the new command prompt.
    :return:
    """
    objTab.Screen.Send('{}{}'.format(variables['boot_command'], end_line))
    objTab.Screen.WaitForString(variables['boot_message'])
    log_message('boot_device: Detected Boot Message!')
    objTab.Screen.Send(end_line)
    log_message('boot_device: Return Pressed!')
    objTab.Screen.WaitForString('[yes/no]:')
    objTab.Screen.Send('no' + end_line)
    log_message('boot_device: Skipping Initial Configuration Dialog')
    change_to_boot_prompt()
    objTab.Screen.WaitForString(variables['prompt'])
    log_message('boot_device: Found Prompt!')


def enable_shell():
    """
    Enable the terminal shell after device has successfully booted.
    :return:
    """
    objTab.Screen.Send('en' + end_line)
    change_to_shell_prompt()
    objTab.Screen.WaitForString(variables['prompt'])
    log_message('enable_shell: Enabled Shell and detected Prompt!')


def delete_file(filename):
    """
    Used to delete a specific file using the del command.
    :param filename: File to be deleted.
    :return: Whether the file was deleted or not.
    """
    log_message('delete_file: Deleting {}'.format(filename))
    objTab.Screen.Send("del /f /r {}{}".format(filename, end_line))
    output_string = objTab.Screen.WaitForStrings(['y/n', 'file or directory'])
    # Check if the output is y/n, and if it is, send a confirmation.
    if output_string == 1:
        objTab.Screen.Send(confirmation)
        objTab.Screen.WaitForString(variables['prompt'])
        log_message('delete_file: File Deleted! {}'.format(filename))
    elif output_string == 2:
        log_message('delete_file: Could not delete file! {}'.format(filename))
        display_to_user('File Couldn\'t be deleted! \n{}'.format(filename))


def boot_delete_file(filename):
    """
    Handle forced recursive deletion of directory contents.
    :param filename: Name of file(or directory) to be deleted
    :return:
    """
    log_message('boot_delete_file: Deleting {}'.format(filename))
    objTab.Screen.Send("del /f /r {}{}".format(filename, end_line))
    objTab.Screen.WaitForString(variables['prompt'])


def write_erase():
    """
    Send the 'write erase' command to the terminal to clear the nvram filesystem
    :return:
    """
    # Send the write erase command
    objTab.Screen.Send("write erase" + end_line)
    log_message('write_erase: Sent write erase command!')
    # Wait for the write erase confirmation prompt and send a carriage return
    objTab.Screen.WaitForStrings('Continue?')
    objTab.Screen.Send(end_line)
    log_message('write_erase: Found Confirmation')
    # Wait for the prompt to appear again.
    objTab.Screen.WaitForString(variables['prompt'])
    log_message('write_erase: Found Prompt!')





def process_directory(files):
    """
    Delete all files that were determined earlier.
    :return:
    """
    # files = get_directory_contents(variables['directory'])
    log_message('process_directory: File List: {}'.format(files))
    try:
        for file in files:
            boot_delete_file(file)
            log_message('process_directory: File deleted! {}'.format(file))
    except Exception as e:
        log_message('process_directory: ERROR: {}'.format(str(e)))


def get_directory_contents(directory):
    """
    Get the contents of a directory and break it down into a list, removing the .bin files
    :param directory: The directory to parse over.
    :return: List of directory contents without the .bin files.
    """
    # Check if the directory exists by calling it using the 'dir' command
    directory_exists = call_directory(directory)
    directory_contents = ''  # Initialize an empty string to store the contents of the directory
    more_count = 0  # Number of times MORE was detected in the directory.
    found_bin_file = False  # Boolean to determine if the .bin file has been detected

    # If the directory was detected, handle determining the contents
    if directory_exists:

        while True:  # The first pass through is for counting how many MORE prompts exist.
            log_message('get_directory_contents: Waiting for MORE')
            # Determine if a MORE prompt exists in the directory content.
            index = objTab.Screen.WaitForStrings(['MORE', variables['prompt']])
            if index == 1:  # If MORE was detected
                more_count += 1  # Increase the counter for the number of MOREs detected
                log_message('get_directory_contents: Found {} MORE(s)'.format(more_count))
                objTab.Screen.Send(" ")  # Send a space after MORE is detected to push prompt forward
            elif index == 2:  # If the prompt was detected
                log_message('get_directory_contents: Found Prompt. {} total MORE(s)'.format(more_count))
                break

        # Call the directory a second time, so that it can be read.
        if call_directory(directory):
            log_message('get_directory_contents: Reading Directory Contents...')

            if more_count == 0:  # Handle the instance where more_count is 0.
                log_message('get_directory_contents: Stubby results with no MOREs for {}'.format(directory))
                # Get all text up until the prompt is detected
                text = objTab.Screen.ReadString(variables['prompt'])
                directory_contents += text + '\n'  # Save text into directory_contents

            for more in range(more_count):  # Iterate over each MORE and add its text to the directory_content
                log_message('get_directory_contents: Reading until MORE {}'.format(more + 1))
                text = objTab.Screen.ReadString('MORE')
                directory_contents += text + '\n'
                objTab.Screen.Send(" ")

        # Split the contents into rows on a new line
        file_rows = directory_contents.split('\n')
        files = []

        log_message('get_directory_contents: Contents have been read. Finding file names in {}'.format(directory))

        # Create a list of dictionary objects
        for row in file_rows:
            # Skip empty lines
            if row.strip():
                # Ignore rows that have a boot extension
                if ".conf" in row or "pkg." in row:
                    found_bin_file = True
                    log_message('get_directory_contents: Found .conf file!')
                    display_to_user('Couldn\'t find .conf file!')
                    continue
                # The last line contains byte information. This can be used as an indication for the end of the loop.
                if 'bytes' in row:
                    break

                # Append a dictionary to files list that contains filenames
                row_info = get_row_info(row, directory)
                if row_info:
                    files.append(row_info)
                else:
                    log_message('get_directory_contents: ERROR: No file found for {}/}|'.format(directory, row))

        if files and found_bin_file:  # If files were detected, return them as a list
            return files
        else:  # If the directory was empty, return None
            log_message('get_directory_contents: No files found in {} directory|'.format(directory))
            return None


def get_row_info(row, directory):
    """
    Reads the contents of a row and returns the filename.
    :param row: The row info to parse
    :param directory: The directory path where the file is located.
    :return:
    """
    entries = row.split()  # Split the row into a list of entries
    short_filename = entries[-1]
    full_filename = directory + '/' + short_filename
    log_message('get_row_info: Filename {}'.format(full_filename))
    return full_filename


def call_directory(directory):
    """
    Get a list of the root directory's contents.
    :return: Boolean determining if the directory existed.
    """
    # Send a command to prompt to display the contents of the directory
    objTab.Screen.Send("dir {}{}".format(directory, end_line))
    log_message('call_directory: Called for directory {}'.format(directory))
    # Wait for confirmation on the existence of the directory.
    check_for_directory = objTab.Screen.WaitForStrings(['Directory of {}/'.format(directory),
                                                       'no such file or directory'])
    # Return a boolean with the existence of the directory.
    if check_for_directory == 1:
        return True
    elif check_for_directory == 2:
        return False


def change_to_rommon_prompt():
    """
    Set the prompt variable to the correct setting for ROMMON commands.
    :return:
    """
    prompt = variables['prompt']
    last_char = prompt[-1]  # Get the last character in the prompt
    # If the final character is a prompt symbol, slice it from prompt to be replaced.
    if last_char == ':' or last_char == '>' or last_char == '#':
        prompt = prompt[:-1]
    prompt = prompt.lower() + ':'
    variables['prompt'] = prompt
    log_message('change_to_rommon_prompt: New Prompt! {}'.format(variables['prompt']))


def change_to_boot_prompt():
    """
    Set the prompt variable to the correct setting after the boot command has been called.
    :return:
    """
    prompt = variables['prompt']
    prompt = prompt[:-1]
    prompt = prompt.capitalize() + '>'
    variables['prompt'] = prompt
    log_message('change_to_boot_prompt: New Prompt! {}'.format(variables['prompt']))


def change_to_shell_prompt():
    """
    Set the prompt variable to the enabled shell terminal prompt
    :return:
    """
    prompt = variables['prompt']
    prompt = prompt[:-1]
    prompt = prompt.capitalize() + '#'
    variables['prompt'] = prompt
    log_message('change_to_shell_prompt: New Prompt! {}'.format(variables['prompt']))


def handle_device():
    """
    Handle the messy art of wiping a Cisco device.
    This handles the logic of device erasure to keep main() clean.
    :return:
    """
    # Start with the ROMMON prompt
    change_to_rommon_prompt()
    # Set configuration to ignore user configuration
    ignore_startup()
    # Get directory contents before boot
    files = get_directory_contents(variables['directory'])
    # Boot the device
    boot_device()
    # Enable the terminal shell
    enable_shell()
    # Send the 'write erase' command
    write_erase()
    #Clear stored logs
    clear_logs()
    # Recursively del nvram: directory
    del_nvram_dir()
    # Format the crashinfo: directory
    format_crash()
    #Check for VTP status then delete VLANs
    check_vtp_vlans()
    # Process the contents of the directory
    process_directory(files)

# clear_logs
# format_crash_dir
# del_nvram_dir
# check_vtp()
# del_vlans
# clear_keys
# save and display hardware/vlan info









# ====================================================================================================================
"""
Clear all stored logs
"""
def clear_logs():
    objTab.Screen.Send("clear log" + end_line)
    log_message('clear_log: Sent clear log command!')
    # Wait for the write erase confirmation prompt and send a carriage return
    objTab.Screen.WaitForStrings('[confirm]')
    objTab.Screen.Send(end_line)
    log_message('clear_log: Found Confirmation')
    # Wait for the prompt to appear again.
    objTab.Screen.WaitForString(variables['prompt'])
    log_message('clear_log: Found Prompt!')

"""
Clear all network keys
"""
def clear_keys():
    objTab.Screen.Send("crypto key zeroize rsa" + end_line)
    objTab.Screen.WaitForString(variables[])
    objTab.Screen.Send("crypto key zeroize rsa" + end_line)


"""
Send the 'conf t' command to enable the configuration terminal
"""
def enable_configuration():
    objTab.Screen.Send("conf t" + end_line)
    change_to_configuration_prompt()
    objTab.Screen.WaitForString(variables['prompt'])
    log_message('enable_configuration: Enabled configuration and detected Prompt!')

"""
Format the 'crashinfo:' directory
"""
def format_crash():
    objTab.Screen.Send("format crashinfo:" + end_line)
    objTab.Screen.WaitForStrings('[confirm]')
    objTab.Screen.Send(end_line)
    log_message('clear_log: Found Confirmation')
    objTab.Screen.WaitForStrings('[confirm]')
    objTab.Screen.Send(end_line)
    log_message('clear_log: Found Confirmation')
    objTab.Screen.WaitforStrings(variables['prompt'])

"""
Delete the contents of nvram dir:
"""
def del_nvram_dir():
    objTab.Screen.Send("del /f /r nvram:")
    objTab.Screen.WaitForStrings(variables['prompt'])
    log_message('del_nvram_dir: Deleted Nvram and Found prompt!')

"""
    Send 'show vtp status' to check and set status to 'OFF'
"""
def check_vtp_vlans():
    objTab.Screen.Send("show vtp status" + end_line)
    response = objTab.Screen.ReadString("Switch#")
    if "Client" in response or "Transparent" in response:
        # If VTP Client or Transparent mode is enabled, turn off VTP mode
        enable_configuration()
        objTab.Screen.Send("vtp mode off" + end_line)
        objTab.Screen.WaitForString(variables['prompt'])
        objTab.Screen.Send("no vlan 2-4094" + end_line)
        objTab.Screen.WaitForString(variables['prompt'])
    elif "OFF" in response:
        enable_configuration()
        objTab.Screen.Send("no vlan 2-4094" + end_line)
        objTab.Screen.WaitForString(variables['prompt'])
        objTab.Screen.Send(end_line)

"""
Switch to the configuration terminal prompt
"""
def change_to_configuration_prompt():
    prompt = variables['prompt']
    prompt = prompt[:-1]
    prompt = prompt.capitalize() + '(config)#'
    variables['prompt'] = prompt
    log_message('change_to_configuration_prompt: New Prompt! {}'.format(variables['prompt']))
"""
Send the 'conf t' command to enable the configuration terminal
"""
def enable_configuration():
    objTab.Screen.Send("conf t" + end_line)
    change_to_configuration_prompt()
    objTab.Screen.WaitForString(variables['prompt'])
    log_message('enable_configuration: Enabled configuration and detected Prompt!')









# ====================================================================================================================

# Main function to run.

# ====================================================================================================================
# ====================================================================================================================


# Call the main function when this script is ran.
main()


# ====================================================================================================================
# ====================================================================================================================

# Graveyard Functions

# ====================================================================================================================
# ====================================================================================================================


# def get_file_indices(row):
#     """
#     Reads the contents of a row to determine which one is the filename.
#     :param row: Row of data to parse.
#     :return: Index with the location of the filename
#     """
#     index = None  # Create an empty reference to the index containing filename
#     row_info = row.split()  # Split the row on the space character.
#     index = row_info.index(row_info[len(row_info) - 1]) # Get the index of the final entry in a row.
#     return index


# Determine boot file
# def boot_var():
#     """
#     Find the current boot variable and
#     """
#     objTab.Screen.Send("set" + end_line)
#     change_to_shell_prompt()
#     boot_file = objTab.Screen.ReadString(variables['prompt'])
#     if "packages.conf" in boot_file or ".bin" in boot_file:

# Erase ROMMON files (first in handle device())
# def rommon_erasure():
#     """
#     Handle file erasures in ROMMON before boot
#     :return:
#     """
#     # Iterate over all the variable ROMMON files and call a delete command on them.
#     # IMPORTANT! This does NOT delete files that are not in the root directory from here!
#     for file in variables['rommon_files']:
#         file_path = variables['directory'] + file
#         delete_file(file_path)
#     log_message('rommon_erasure: Complete!')