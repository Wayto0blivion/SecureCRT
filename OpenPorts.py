# $language = "python"
# $interface = "1.0"


crt.Screen.Send("conf t")
crt.Screen.Send(chr(13))
crt.Sleep(100)

#crt.Screen.Send("int ethernet 1/1")

for port in range(1, 55):
    crt.Screen.Send("int ethernet 1/" + str(port))
    crt.Screen.Send(chr(13))
    crt.Sleep(500)
    crt.Screen.Send("no shut")
    crt.Screen.Send(chr(13))
    crt.Sleep(200)
    crt.Screen.Send("ex")
    crt.Screen.Send(chr(13))
    crt.Sleep(200)

crt.Screen.Send("end")
crt.Screen.Send(chr(13))








