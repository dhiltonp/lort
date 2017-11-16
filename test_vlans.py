import pytest

import vlans
from vlans import vlans_parser


def test_vlans_parser():
    vlans = vlans_parser('1')
    assert len(vlans) == 1
    assert vlans[0] == 1

    vlans = vlans_parser('1-10')
    assert len(vlans) == 10
    assert vlans[0] == 1
    assert vlans[9] == 10

    vlans = vlans_parser('5-24,50-69')
    assert len(vlans) == 40
    assert vlans[0] == 5
    assert vlans[39] == 69


def test_validate_vlan_range():
    errors = vlans.validate_vlan_range([-1])
    assert len(errors) == 1
    assert errors[0] == 'lowest vlan (-1) < 2'

    errors = vlans.validate_vlan_range([255])
    assert len(errors) == 1
    assert errors[0] == 'highest vlan (255) > 250'

    vlans.validate_vlan_range(range(2, 251))

