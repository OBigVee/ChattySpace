
def test_createAccount(chat, accounts):
    assert chat.createAccount("kenneth", {'from': accounts[0]})

def test_getUsername(chat, accounts):
    assert chat.createAccount("kenneth", {'from': accounts[0]})
    assert chat.getUsername(accounts[0], {'from': accounts[0]}) == "kenneth"

def test_addFriend(chat, accounts):
    assert chat.createAccount("kenneth", {'from': accounts[0]})
    assert chat.createAccount("Benny", {'from': accounts[1]})
    assert chat.addFriend(accounts[1], "Benny", {'from': accounts[0]})

def test_getMyFriendLists(chat, accounts):
    assert chat.createAccount("kenneth", {'from': accounts[0]})
    assert chat.createAccount("Benny", {'from': accounts[1]})
    assert chat.addFriend(accounts[1], "Benny", {'from': accounts[0]})
    x = chat.getMyFriendLists({'from': accounts[0]})
    assert x[0] == ("Benny", accounts[1])

def test_sendMessage(chat, accounts):
    assert chat.sendMessage(accounts[1], "hello", {'from': accounts[0]})

def test_readMessage(chat, accounts, chain):
    assert chat.sendMessage(accounts[1], "hello", {'from': accounts[0]})
    assert chat.readMessage(accounts[1], {'from': accounts[0]}) == (accounts[0], chain[-1].timestamp, "hello")
