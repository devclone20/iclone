// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./AgentVault.sol";

/// @title AgentVaultFactory
/// @notice Entry point to fractionalize an iCLONE agent NFT. Deploys one
///         AgentVault per agent, pulls the NFT in, mints shares to the owner.
/// @dev    Reference implementation — audit before mainnet.
contract AgentVaultFactory is Ownable {
    IERC721 public immutable agentNFT;

    address public feeSink;   // Splitter (3x10% rails) or address(0)
    uint16  public feeBps;    // protocol fee applied by each vault (<=10%)

    mapping(uint256 => address) public vaultOf;   // tokenId => vault

    event Fractionalized(
        uint256 indexed tokenId,
        address indexed vault,
        address indexed curator,
        address operator,
        uint256 supply,
        uint256 reservePrice
    );
    event FeeConfig(address feeSink, uint16 feeBps);

    constructor(address _agentNFT, address _feeSink, uint16 _feeBps) Ownable(msg.sender) {
        require(_agentNFT != address(0), "nft=0");
        require(_feeBps <= 1_000, "fee too high");
        agentNFT = IERC721(_agentNFT);
        feeSink = _feeSink;
        feeBps = _feeBps;
    }

    /// @notice Lock `tokenId` and mint `supply` shares. Caller must own the NFT
    ///         and have approved this factory (or set approvalForAll).
    function fractionalize(
        uint256 tokenId,
        uint256 supply,
        uint256 reservePrice,
        address operator,
        string calldata name_,
        string calldata symbol_
    ) external returns (address vault) {
        require(vaultOf[tokenId] == address(0), "already fractional");
        require(agentNFT.ownerOf(tokenId) == msg.sender, "not owner");

        vault = address(new AgentVault(
            address(agentNFT),
            tokenId,
            msg.sender,            // curator = the fractionalizer
            operator,              // who runs the agent (defaults to curator if 0)
            supply,
            reservePrice,
            feeSink,
            feeBps,
            name_,
            symbol_
        ));

        vaultOf[tokenId] = vault;
        // pull the NFT into the vault (requires prior approval)
        agentNFT.safeTransferFrom(msg.sender, vault, tokenId);

        emit Fractionalized(tokenId, vault, msg.sender, operator, supply, reservePrice);
    }

    function setFeeConfig(address _feeSink, uint16 _feeBps) external onlyOwner {
        require(_feeBps <= 1_000, "fee too high");
        feeSink = _feeSink;
        feeBps = _feeBps;
        emit FeeConfig(_feeSink, _feeBps);
    }
}
