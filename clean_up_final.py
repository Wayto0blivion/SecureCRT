# $language = "python"
# $interface = "1.0"

"""
5-9-24 Created by Mitch Kelley - *Credit to Dustin Beck for CRT variables*
clean_up.python

This is a temporary script to be used after boot to finish erasing and saving new changes 
to the NVRAM of Cisco devices.

"""

# Set CRT variables
objTab = crt.GetScriptTab()
objTab.Screen.Synchronous = True
objTab.Screen.IgnoreEscape = True
end_line = chr(13)
confirmation = end_line  # Set a default confirmation variable

# Check if VTP Client or Transparent mode is enabled
objTab.Screen.Send("show vtp status" + end_line)
response = objTab.Screen.ReadString("Switch#")
if "Client" in response or "Transparent" in response:
    # If VTP Client or Transparent mode is enabled, turn off VTP mode
    objTab.Screen.Send("conf t" + end_line)
    objTab.Screen.WaitForString("Switch(config)#")
    objTab.Screen.Send("vtp mode off" + end_line)
    objTab.Screen.WaitForString("Switch(config)#")
    objTab.Screen.Send("exit" + end_line)
    
# List of commands to finish erasing the device
commands = [
    "clear log",
    "",
    "conf t",
    "crypto key zeroize rsa",
    "y",
    "crypto key zeroize ec",
    "y",
    "no vlan 2-4094",
    "exit"]

for command in commands:
    objTab.Screen.Send(command + end_line)

# Command to save changes
objTab.Screen.WaitForString("Switch#")
objTab.Screen.Send("copy running-config startup-config" + end_line)
objTab.Screen.Send(end_line)

# Display vlans to confirm erasure
objTab.Screen.WaitForString("Switch#")
objTab.Screen.Send("show vlan" + end_line)

# Wait for next page prompt
objTab.Screen.WaitForString("--More--")
objTab.Screen.Send(" ")

# List of commands to display hardware and PID
show = [
    "",
    "show env all",
    "show inv"]

for shows in show:
    objTab.Screen.Send(shows + end_line)

    
  
    
    

    
    
  
    
   
    
    
    
    
    
  

    
    
    
    
    