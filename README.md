# discard-server-chat
A terminal-based server chat with the ability to create channels and manage its users. Mark: 10

## Program preview
![DiscardExampleChat](https://github.com/artHub-j/discard-server-chat/assets/92806890/450822a6-d4d3-4ddc-a491-bbf2d125ef66)

## All possible commands
<p align="center">
<img src="https://github.com/artHub-j/discard-server-chat/assets/92806890/f13659a0-d707-43f2-821c-8f18792bb260" width="500"/>
</p>

## Usage

### 0. Clone the repo:
```
git clone https://github.com/artHub-j/discard-server-chat.git
cd discard-server-chat
```

### 1. Modify Client_Multicanal_TCP.py file:
Modify line 57 of the Client_Multicanal_TCP.py file and change the given IP to the IP of the device where the server was opened
```
serverName = 'pcserverip'
```

### 2. Open the Server in Terminal:
```
python3 Server_Multicanal_TCP.py
```

### 3. Create a User and join as Client (in a new Terminal):
```
python3 Cliente_Multicanal_TCP.py
```

### 4. Keep repeating process 3 to add new Clients (in new Terminals):
```
python3 Cliente_Multicanal_TCP.py
```

