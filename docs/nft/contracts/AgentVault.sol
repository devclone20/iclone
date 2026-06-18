// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @title AgentVault
/// @notice Fractional ownership + revenue share for ONE iCLONE agent NFT.
///         The vault holds the agent NFT and is itself the ERC-20 shares token.
///         Economics (shares, revenue, buyout) are split from control (operator),
///         so the agent keeps running while owned by many.
/// @dev    Reference implementation — MUST be audited before any mainnet deploy.
contract AgentVault is ERC20, IERC721Receiver, ReentrancyGuard {
    IERC721 public immutable agentNFT;
    uint256 public immutable tokenId;

    address public curator;       // governs the vault; can rotate operator / reserve
    address public operator;      // runs the agent; runtime authenticates against this
    uint256 public reservePrice;  // full buyout price (wei)

    bool    public bought;        // true after a successful buyout
    uint256 public buyoutPool;    // ETH locked for redemption
    uint256 public supplyAtBuyout;

    // --- magnified-dividend accounting (ETH), pull-based, no holder loops ---
    uint256 internal constant MAG = 2**128;
    uint256 internal magPerShare;
    mapping(address => int256)  internal magCorrection;
    mapping(address => uint256) public withdrawn;

    event Distributed(uint256 amount, uint256 fee);
    event Claimed(address indexed who, uint256 amount);
    event Buyout(address indexed buyer, uint256 price);
    event Redeemed(address indexed who, uint256 shares, uint256 eth);
    event OperatorChanged(address indexed operator);
    event CuratorChanged(address indexed curator);
    event ReservePriceChanged(uint256 reservePrice);

    // optional protocol fee on distribute/buyout, routed to the Splitter
    address public feeSink;       // Splitter (3x10% rails) or address(0)
    uint16  public feeBps;        // e.g. 100 = 1%
    uint16  public constant BPS = 10_000;

    modifier onlyCurator() { require(msg.sender == curator, "not curator"); _; }

    constructor(
        address _nft,
        uint256 _tokenId,
        address _curator,
        address _operator,
        uint256 _supply,
        uint256 _reservePrice,
        address _feeSink,
        uint16  _feeBps,
        string memory name_,
        string memory symbol_
    ) ERC20(name_, symbol_) {
        require(_curator != address(0), "curator=0");
        require(_supply > 0, "supply=0");
        require(_feeBps <= 1_000, "fee too high"); // hard cap 10%
        agentNFT = IERC721(_nft);
        tokenId = _tokenId;
        curator = _curator;
        operator = _operator == address(0) ? _curator : _operator;
        reservePrice = _reservePrice;
        feeSink = _feeSink;
        feeBps = _feeBps;
        _mint(_curator, _supply); // curator gets 100% of shares to distribute/sell
    }

    function onERC721Received(address, address, uint256, bytes calldata)
        external pure returns (bytes4) { return IERC721Receiver.onERC721Received.selector; }

    // ───────────────────────── revenue ─────────────────────────

    receive() external payable { _distribute(msg.value); }

    /// @notice Send agent revenue (ETH) to be shared pro-rata with holders.
    function distribute() external payable { _distribute(msg.value); }

    function _distribute(uint256 amount) internal {
        require(!bought, "bought out");
        require(totalSupply() > 0, "no shares");
        require(amount > 0, "zero");
        uint256 fee = (feeSink != address(0) && feeBps > 0) ? amount * feeBps / BPS : 0;
        if (fee > 0) { (bool ok,) = feeSink.call{value: fee}(""); require(ok, "fee send"); }
        uint256 net = amount - fee;
        magPerShare += net * MAG / totalSupply();
        emit Distributed(net, fee);
    }

    function cumulativeOf(address a) public view returns (uint256) {
        int256 c = int256(magPerShare * balanceOf(a)) + magCorrection[a];
        return uint256(c) / MAG;
    }

    function claimable(address a) public view returns (uint256) {
        return cumulativeOf(a) - withdrawn[a];
    }

    function claim() external nonReentrant {
        uint256 amount = claimable(msg.sender);
        require(amount > 0, "nothing");
        withdrawn[msg.sender] += amount;
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok, "claim send");
        emit Claimed(msg.sender, amount);
    }

    /// @dev settle dividend corrections on mint / burn / transfer
    function _update(address from, address to, uint256 value) internal override {
        super._update(from, to, value);
        int256 corr = int256(magPerShare * value);
        if (from != address(0)) magCorrection[from] += corr;
        if (to   != address(0)) magCorrection[to]   -= corr;
    }

    // ───────────────────────── buyout ─────────────────────────

    /// @notice Buy out the whole agent: NFT goes to the buyer, holders redeem the pool.
    function buyout() external payable nonReentrant {
        require(!bought, "already bought");
        require(msg.value >= reservePrice, "below reserve");
        bought = true;
        supplyAtBuyout = totalSupply();

        uint256 fee = (feeSink != address(0) && feeBps > 0) ? msg.value * feeBps / BPS : 0;
        if (fee > 0) { (bool ok,) = feeSink.call{value: fee}(""); require(ok, "fee send"); }
        buyoutPool = msg.value - fee;

        agentNFT.safeTransferFrom(address(this), msg.sender, tokenId);
        operator = msg.sender; // buyer now controls the agent
        emit Buyout(msg.sender, msg.value);
        emit OperatorChanged(msg.sender);
    }

    /// @notice After a buyout, burn shares to redeem pro-rata ETH.
    function redeem(uint256 shares) external nonReentrant {
        require(bought, "not bought");
        require(shares > 0, "zero");
        uint256 eth = buyoutPool * shares / supplyAtBuyout;
        _burn(msg.sender, shares);
        (bool ok,) = msg.sender.call{value: eth}("");
        require(ok, "redeem send");
        emit Redeemed(msg.sender, shares, eth);
    }

    // ───────────────────────── governance ─────────────────────────

    function setOperator(address op) external onlyCurator {
        require(op != address(0), "op=0");
        operator = op;
        emit OperatorChanged(op);
    }

    function setReservePrice(uint256 p) external onlyCurator {
        require(!bought, "bought");
        reservePrice = p;
        emit ReservePriceChanged(p);
    }

    function transferCurator(address c) external onlyCurator {
        require(c != address(0), "curator=0");
        curator = c;
        emit CuratorChanged(c);
    }
}
