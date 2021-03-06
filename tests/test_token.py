import pytest
from brownie import accounts, Eventoken
import brownie

TOTAL_SUPPLY = 5000
NAME = "ChattyPoint"
SYMBOL = "CP"
DECIMALS = 0


@pytest.fixture(autouse=True)
def eventoken():
    token = accounts[0].deploy(Eventoken, NAME, SYMBOL, TOTAL_SUPPLY)
    _user1, _user2 = "OVECJOE", "B_Keys"
    token.createToken(_user1, {'from': accounts[1], 'value': '2'})
    token.createToken(_user2, {'from': accounts[2], 'value': '2'})
    return token


def test_init(eventoken):
    assert eventoken.usernames("Minter") == eventoken.contract_owner()
    assert eventoken.totalSupply() == TOTAL_SUPPLY
    assert eventoken.name() == NAME
    assert eventoken.symbol() == SYMBOL
    assert eventoken.decimals() == DECIMALS


def test_create_token(eventoken):
    _username = 'OVECJOE'
    with brownie.reverts('Username already exists!'):
        eventoken.createToken(_username, {'from': accounts[2], 'value': '2'})
    assert eventoken.usernames(_username) == accounts[1].address
    assert eventoken.tokens(accounts[1])['owner'] == accounts[1].address
    assert eventoken.tokens(accounts[1])['point_balance'] == 0
    assert len(_username) >= 6


def test_transfer_revert(eventoken):
    with brownie.reverts("Insufficient Balance!"):
        eventoken.transfer(accounts[1], 100, {'from': accounts[2]})
    with brownie.reverts("Cannot send points to the same address!"):
        eventoken.transfer(accounts[0], 100, {'from': accounts[0]})


def test_mine_points(eventoken):
    with brownie.reverts("You can only mine for yourself!"):
        eventoken.mine(accounts[1], {'from': accounts[2]})
    with brownie.reverts("Contract owner is not permitted to mine!"):
        eventoken.mine(accounts[0], {'from': accounts[0]})
    eventoken.mine(accounts[1], {'from': accounts[1]})
    eventoken.mine(accounts[2], {'from': accounts[2]})
    assert eventoken.balanceOf(accounts[1]) > 0
    assert eventoken.balanceOf(accounts[2]) > 0
    return eventoken


def test_mint(eventoken):
    with brownie.reverts("You do not have 'mint' privilege!"):
        eventoken.mint(accounts[1], 40, {'from': accounts[1]})
    with brownie.reverts("Only the deployer can mint for others!"):
        eventoken.mint(accounts[0], 10000, {'from': accounts[0]})
    with brownie.reverts("Point Balance must be >= 10CP!"):
        eventoken.mint(accounts[1], 101, {'from': accounts[0]})
    eventoken = test_mine_points(eventoken)
    with brownie.reverts("Too small; must be >= 20CP!"):
        eventoken.mint(accounts[1], 12, {'from': accounts[0]})

    balance = eventoken.balanceOf(accounts[2])
    eventoken.mint(accounts[2], 50, {'from': accounts[0]})
    assert eventoken.balanceOf(accounts[2]) - balance > 0


def test_approve(eventoken):
    eventoken = test_mine_points(eventoken)
    with brownie.reverts():
        eventoken.approve(accounts[2], 100, {'from': accounts[2]})
        eventoken.approve(accounts[0], 100, {'from': accounts[1]})
        eventoken.approve(accounts[1], 100, {'from': accounts[0]})
    eventoken.approve(accounts[1], 100, {'from': accounts[2]})
    assert eventoken.allowance(accounts[2], accounts[1]) == 100


def test_increase_approval(eventoken):
    eventoken = test_mine_points(eventoken)
    with brownie.reverts():
        eventoken.increaseApproval(accounts[2], 100, {'from': accounts[2]})
        eventoken.increaseApproval(accounts[0], 100, {'from': accounts[1]})
        eventoken.increaseApproval(accounts[1], 100, {'from': accounts[0]})
    allowance = eventoken.allowance(accounts[2], accounts[1])
    eventoken.increaseApproval(accounts[1], 200, {'from': accounts[2]})
    assert eventoken.allowance(accounts[2], accounts[1]) - allowance == 200


def test_decrease_approval(eventoken):
    eventoken = test_mine_points(eventoken)
    with brownie.reverts():
        eventoken.decreaseApproval(accounts[2], 100, {'from': accounts[2]})
        eventoken.decreaseApproval(accounts[0], 100, {'from': accounts[1]})
        eventoken.decreaseApproval(accounts[1], 100, {'from': accounts[0]})
    allowance = eventoken.allowance(accounts[2], accounts[1])
    eventoken.decreaseApproval(accounts[1], 100, {'from': accounts[2]})
    assert eventoken.allowance(accounts[2], accounts[1]) - allowance == 0


def test_transfer(eventoken):
    eventoken = test_mine_points(eventoken)
    p_bal1 = eventoken.balanceOf(accounts[1])
    p_bal2 = eventoken.balanceOf(accounts[2])

    eventoken.transfer(accounts[1], 100, {'from': accounts[2]})
    assert eventoken.balanceOf(accounts[1]) == p_bal1 + 100
    assert eventoken.balanceOf(accounts[2]) == p_bal2 - 100


def test_delete(eventoken):
    eventoken = test_mine_points(eventoken)
    with brownie.reverts("MegaTron does not exists!"):
        eventoken.delete('MegaTron')
    with brownie.reverts("Minter is not active!"):
        eventoken.delete('Minter')

    address = eventoken.usernames('B_Keys')
    bal = eventoken.balanceOf(address)
    total_supply = eventoken.totalSupply() - bal

    assert bal > 0
    eventoken.delete('B_Keys')
    assert eventoken.balanceOf(address) == 0
    assert eventoken.totalSupply() == total_supply

    with brownie.reverts('B_Keys does not exists!'):
        eventoken.delete('B_Keys')
