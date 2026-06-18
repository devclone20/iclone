// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @title iCLONE Treasury Splitter
/// @notice Routes mint/skill revenue across the 3x10% rails + ops remainder.
///         All movements are on-chain and auditable.
///   - 10% -> BTC reserve (held as cbBTC on Base)
///   - 10% -> VIRTUAL (liquidity/treasury)
///   - 10% -> iCLONE buyback & burn
///   - remainder (70%) -> ops/creator
/// Swaps to cbBTC / VIRTUAL / iCLONE are executed by `harvest()` callers (keeper),
/// keeping this contract a simple, auditable accounting + routing layer.
contract Splitter is Ownable, ReentrancyGuard {
    uint16 public constant BPS = 10_000;
    uint16 public btcBps     = 1_000; // 10%
    uint16 public virtualBps = 1_000; // 10%
    uint16 public icloneBps  = 1_000; // 10%

    address public btcSink;     // cbBTC accumulation / reserve
    address public virtualSink; // VIRTUAL treasury
    address public icloneSink;  // buyback&burn module
    address public opsSink;     // remainder

    event Routed(uint256 total, uint256 btc, uint256 virtuals, uint256 iclone, uint256 ops);
    event SinksUpdated(address btc, address virtuals, address iclone, address ops);

    constructor(address _btc, address _virtual, address _iclone, address _ops)
        Ownable(msg.sender)
    {
        _setSinks(_btc, _virtual, _iclone, _ops);
    }

    receive() external payable { _route(msg.value); }

    function _route(uint256 amount) internal nonReentrant {
        if (amount == 0) return;
        uint256 btc      = amount * btcBps / BPS;
        uint256 virtuals = amount * virtualBps / BPS;
        uint256 iclone   = amount * icloneBps / BPS;
        uint256 ops      = amount - btc - virtuals - iclone;

        _send(btcSink, btc);
        _send(virtualSink, virtuals);
        _send(icloneSink, iclone);
        _send(opsSink, ops);

        emit Routed(amount, btc, virtuals, iclone, ops);
    }

    function _send(address to, uint256 v) internal {
        if (v == 0) return;
        (bool ok, ) = to.call{value: v}("");
        require(ok, "send failed");
    }

    function setSinks(address _btc, address _virtual, address _iclone, address _ops)
        external onlyOwner
    {
        _setSinks(_btc, _virtual, _iclone, _ops);
    }

    function _setSinks(address _btc, address _virtual, address _iclone, address _ops) internal {
        require(_btc != address(0) && _virtual != address(0) && _iclone != address(0) && _ops != address(0), "sink=0");
        btcSink = _btc; virtualSink = _virtual; icloneSink = _iclone; opsSink = _ops;
        emit SinksUpdated(_btc, _virtual, _iclone, _ops);
    }
}
