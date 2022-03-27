# @version ^0.3.1

# Each friend is identified by its address and name assigned by the second party
struct friend:
    name: String[50]
    pubkey: address

# Stores the default name of an user and her friends info
struct user:
    name: String[50]
    friendList: friend[100]

# message struct stores the single chat message and its metadata
struct message:
    sender: address
    _timestamp: uint256
    _msg: String[100]

# post struct stores the single post and its metadata
struct post:
    sender: address
    _timestamp: uint256
    _post: String[100]
    
# Collection of users registered on the application
userList: HashMap[address, user]

# Collection of messages communicated in a channel between two users
allMessages: HashMap[bytes32, message]

# Collection of messages communicated in a channel between two users
allPosts: HashMap[bytes32, post]

# It checks whether a user(identified by its public key)
# has created an account on this application or not    
@internal   # function can be called via transactions or from other contracts
@view        # function ca read from the contract state, but does not alter it
def checkUserExists(_pubkey: address) -> bool :
    bytes_string: Bytes[50] = convert(self.userList[_pubkey].name, Bytes[50])
    return len(bytes_string) > 0

# Registers the caller(msg.sender) to our app with a non-empty username
@external
def createAccount(_username: String[50]):

    assert self.checkUserExists(msg.sender) == False, "User already exists!"
    assert len(convert(_username, Bytes[50])) > 0, "Username cannot be empty!"
    self.userList[msg.sender].name = _username

# returns the default name provided by the user
@view       #function ca read from the contract state, but does not alter it
@external
def getUsername(_pubkey: address) -> String[50]:
    assert self.checkUserExists(_pubkey) == True, "User is not Registered"
    return self.userList[_pubkey].name

# Checks if two users are already friends or not
@internal
@view
def checkAlreadyfriends(_pubkey1: address, _pubkey2: address) -> bool:
    for i in range(100):
        exam: friend = self.userList[_pubkey1].friendList[i]
        if exam.pubkey == _pubkey2:
            return True
    return False

# A helper function to update the friendList
@internal
def _addFriend(me: address, _friend_key: address, _username: String[50]):
    Index: uint256 = 0

    newFriend: friend = friend({name: _username, pubkey: _friend_key})
    self.userList[me].friendList[Index] = newFriend
    Index += 1

# Adds new user as your friend with an associated nickname
@external
def addFriend(_friend_key: address, _username: String[50]):
    assert self.checkUserExists(msg.sender) == True, "Create an account first"
    assert self.checkUserExists(_friend_key) == True, "User not resgistered"
    assert msg.sender != _friend_key, "Users cannot add themselves as friends"
    assert self.checkAlreadyfriends(msg.sender, _friend_key) == False, "Users are already friends"

    self._addFriend(msg.sender, _friend_key, _username)
    self._addFriend(_friend_key, msg.sender, self.userList[msg.sender].name)


# Returns list of friends of the sender
@external
@view
def getMyFriendLists() -> friend[100]:
    return self.userList[msg.sender].friendList


# Returns a unique code for the channel created between the two users
# Hash(key1,key2) where key1 is lexicographically smaller than key2
@internal
@pure # does not read from the contract state or environmental variable
def _getChatCode(_pubkey1: address, _pubkey2: address) -> bytes32:
    if convert(_pubkey1, uint256) > convert(_pubkey2, uint256):
        return keccak256(_abi_encode(_pubkey1, _pubkey2, method_id=method_id("_getChatCode()")))
    else:
        return keccak256(_abi_encode(_pubkey2, _pubkey1, method_id=method_id("_getChatCode()")))

# Send new message to a given friend
@external
def sendMessage(_friend_key: address, _msg: String[100]):
    assert self.checkUserExists(msg.sender) == False, "Create an account first"
    assert self.checkUserExists(_friend_key) == False, "User not registered yet"
    assert self.checkAlreadyfriends(msg.sender, _friend_key) == False, "Not friends with user"

    chatcode: bytes32 = self._getChatCode(msg.sender, _friend_key)
    newMsg: message = message({sender: msg.sender, _timestamp: block.timestamp, _msg: _msg})
    self.allMessages[chatcode] = newMsg

# Returns all chat messages communicated in channel
@view
@external
def readMessage(_friend_key: address) -> message:
    chatcode: bytes32 = self._getChatCode(msg.sender, _friend_key)
    return self.allMessages[chatcode]

@internal
@pure # does not read from the contract state or environmental variable
def _getPostId(_pubkey1: address) -> bytes32:
    return keccak256(_abi_encode(_pubkey1, method_id=method_id("_getChatCode()")))

# creates a new post
@external
def createPost(_post: String[100]):
    assert self.checkUserExists(msg.sender) == False, "Create an account first"
    
    postId: bytes32 = self._getPostId(msg.sender)
    newPost: post = post({sender: msg.sender, _timestamp: block.timestamp, _post: _post})
    self.allPosts[postId] = newPost

# Returns all Posts made by users.
@view
@external
def getPosts() -> post:
    postId: bytes32 = self._getPostId(msg.sender)
    return self.allPosts[postId]