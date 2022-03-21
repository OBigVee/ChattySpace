# @version ^0.3.1

# This token contract follows the ERC20 standard for tokens.
from vyper.interfaces import ERC20
implements: ERC20

# Events
#   - This event logs that an address has been granted access
#       to an amount of tokens from another.
event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

#   - This event logs that the sender has transfered an amount of tokens
#        to an address.
event Transfer:
    sender: indexed(address)
    reciever: indexed(address)
    value: uint256

#   - This event logs that the owner of the contract has successfully minted
#       a certain amount of tokens to an address.
event Mint:
    reciever: indexed(address)
    value: uint256

#   - This event logs that the current address is mining a random
#       amount of tokens that depends on the address id.
event Mine:
    benefactor: indexed(address)
    value: uint256

#   - This event logs that an address account has been deleted/deactivated
#       from the blockchain.
event Delete:
    victim: indexed(address)
    username: String[32]
    point_balance: uint256

# Storage Variables
name: public(String[32]) # Name of the token contract
symbol: public(String[8]) # Symbol of token contract
decimals: public(uint256) # Number of decimal places
totalSupply: public(uint256) # Total points
contract_owner: public(address) # The deployer

struct token:
    owner_id: uint256
    owner: address
    date_created: uint256 # The owner's username
    point_balance: uint256 # The owner's balance
    is_active: bool # If owner's token is active
    percent_worth: decimal

tokens: public(HashMap[address, token]) # owner_address/token pair.
# Each address can allow other addresses to spend an amount of tokens
allowances: HashMap[address, HashMap[address, uint256]]
usernames: public(HashMap[String[32], address]) # username/address pair.

# Functions
@external
def __init__(_name: String[32], _symbol: String[8], _total_supply: uint256):
    """
    Initializes the storage variables with default values that may not be changed
    during the lifecycle of the contract.
    """
    self.name = _name
    self.symbol = _symbol
    self.decimals = 0
    self.totalSupply = _total_supply
    self.contract_owner = msg.sender
    self.usernames["Minter"] = msg.sender

    log Transfer(ZERO_ADDRESS, msg.sender, _total_supply)

@internal
def _create_token(_owner: address, _username: String[32]) -> token:
    assert _owner != self.contract_owner, "Using minter's address is disallowed!"
    assert self.tokens[_owner] == empty(token), "Account already exists for that address!"
    self.usernames[_username] = _owner
    time: uint256 = block.timestamp
    return token({
        owner_id: shift(time, convert(len(_username), int256)) +
         convert(sha256(_username), uint256),
        owner: _owner,
        date_created: time,
        point_balance: 0,
        is_active: True,
        percent_worth: 0.0
    })

@external
@payable
def createToken(_username: String[32]) -> bool:
    assert len(_username) >= 6, "Length of username must be >= 6"
    assert msg.value == 2, "Creating token costs 2 ChattyPoint!"
    assert self.usernames[_username] == empty(address), "Username already exists!"

    time: uint256 = block.timestamp
    self.tokens[msg.sender] = self._create_token(msg.sender, _username)
    self.usernames[_username] = msg.sender

    return True

@view
@external
def balanceOf(_token_owner: address) -> uint256:
    return self.tokens[_token_owner].point_balance

@view
@external
def allowance(_owner: address, _spender: address) -> uint256:
    return self.allowances[_owner][_spender]

@external
def approve(_spender: address, _value: uint256) -> bool:
    assert _spender != msg.sender and _spender != self.contract_owner\
    and msg.sender != self.contract_owner
    assert self.tokens[_spender].is_active == True, "Address is not active!"

    self.allowances[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True

@external
def increaseApproval(_spender: address, _addedValue: uint256) -> bool:
    assert _spender != msg.sender and _spender != self.contract_owner\
    and msg.sender != self.contract_owner
    assert self.tokens[_spender].is_active == True, "Address is not active!"

    self.allowances[msg.sender][_spender] += _addedValue
    log Approval(msg.sender, _spender, self.allowances[msg.sender][_spender])
    return True

@external
def decreaseApproval(_spender: address, _subtractedValue: uint256) -> bool:
    assert _spender != msg.sender and _spender != self.contract_owner\
    and msg.sender != self.contract_owner
    assert self.tokens[_spender].is_active == True, "Address is not active!"

    oldValue: uint256 = self.allowances[msg.sender][_spender]

    if _subtractedValue > oldValue:
        self.allowances[msg.sender][_spender] = 0
    else:
        self.allowances[msg.sender][_spender] -= _subtractedValue
    
    log Approval(msg.sender, _spender, self.allowances[msg.sender][_spender])
    return True

@internal
def _compute_percent_worth(_addr: address) -> decimal:
    return (convert(self.tokens[_addr].point_balance*100, decimal)
    )/convert(self.totalSupply, decimal)

@internal
def _transfer(_from: address, _to: address, _value: uint256):
    """
    @dev Internal shared logic for transfer and transferFrom
    """
    assert (_from != self.contract_owner) or (_to != self.contract_owner),\
     "Minter can't partake in transfers!"
    assert self.tokens[_from].point_balance >= _value, "Insufficient Balance!"

    self.tokens[_from].point_balance -= _value
    self.tokens[_from].percent_worth = self._compute_percent_worth(_from)
    self.tokens[_to].point_balance += _value
    self.tokens[_to].percent_worth = self._compute_percent_worth(_to)

    log Transfer(_from, _to, _value)

@external
def transfer(_to: address, _value: uint256) -> bool:
    assert _to != msg.sender, "Cannot send points to the same address!"
    assert (self.tokens[_to] != empty(token)),\
     "Restricted; Check address properly!"

    self._transfer(msg.sender, _to, _value)
    return True

@external
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    assert _from != _to, "Cannot send points to the same address!"
    assert (self.tokens[msg.sender] != empty(token)) and (self.tokens[_to] != empty(token)),\
     "Restricted; Check address properly!"
    assert _to != msg.sender, "Restricted; Check address properly!"
    assert self.allowances[_from][msg.sender] >= _value, "Insufficient Allowance!"

    self.allowances[_from][msg.sender] -= _value
    self._transfer(_from, _to, _value)
    return True

@external
def mint(_to: address, amount: uint256) -> bool:
    assert self.contract_owner == msg.sender, "You do not have 'mint' privilege!"
    assert self.contract_owner != _to,\
    "Only the deployer can mint for others!"
    assert amount >= 20, "Too small; must be >= 20CP!"
    assert self.tokens[_to].point_balance >= 10, "Point Balance must be >= 10CP!"
    # assert block.timestamp >= self.tokens[_to].date_created + 86400,\
    # "Minting can only be performed for accounts >= 1 day!"
    assert self.tokens[_to].is_active == True, "Address is not active!"

    self.totalSupply += amount
    self.tokens[_to].point_balance += amount
    self.tokens[_to].percent_worth = self._compute_percent_worth(_to)

    log Mint(_to, amount)
    return True

@external
def mine(_to: address):
    assert _to == msg.sender, "You can only mine for yourself!"
    assert msg.sender != self.contract_owner, "Contract owner is not permitted to mine!"
    assert self.tokens[_to].point_balance < 100, "Request minting from the contract owner."

    _id: uint256 = self.tokens[_to].owner_id
    for i in range(0, 100):
        temp: uint256 = uint256_addmod(_id, i, 2000)
        if ((i * temp) >= 50) and ((i * temp) <= 2000):
            self.tokens[_to].point_balance += (i*temp)
            self.totalSupply += (i*temp)
            self.tokens[_to].percent_worth = self._compute_percent_worth(_to)

            log Mine(_to, i*temp)
            break


@external
def delete(_username: String[32]):
    # The username is used to look up the address, so this ensures that it exists
    assert self.usernames[_username] != empty(address),\
    concat(_username, " does not exists!")

    _victim: address = self.usernames[_username]
    _pb: uint256 = self.tokens[_victim].point_balance

    assert self.tokens[_victim].is_active == True,\
    concat(_username, " is no longer active!")

    self.usernames[_username] = empty(address)
    self.totalSupply -= self.tokens[_victim].point_balance
    self.tokens[_victim] = empty(token)
    
    log Delete(_victim, _username, _pb)
