// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @title iCLONE Agent
/// @notice The NFT IS the agent. ownerOf(tokenId) is the sole controller of that agent.
///         Each token fuses an on-chain silhouette (image) with a neural_soul.md (Arweave)
///         into a single non-fungible key. The genome lets the exact art be re-derived.
contract iCloneAgent is ERC721URIStorage, ERC2981, Ownable, ReentrancyGuard {
    /// @dev Deterministic provenance of the silhouette. Art = render(genome).
    struct Genome {
        uint8  concept;      // 0..9 base concept (UNIX, iCLONE, MATRIX, ...) or >9 custom
        uint8  tier;         // 0 rare, 1 superrare, 2 iclone
        uint32 seed;         // PRNG seed -> deterministic silhouette
        uint16 accessories;  // bitmap: hat|cig|helmet|shoulder|weapon|pc|vivid
    }

    uint256 public nextId;
    uint256 public mintPrice = 0.08 ether;
    address public treasury;            // the Splitter (3x10% rails)

    mapping(uint256 => Genome) public genomeOf;
    mapping(uint256 => string) public soulOf;   // ar://<txid>/neural_soul.md

    event AgentMinted(
        uint256 indexed id,
        address indexed owner,
        Genome  genome,
        string  soulURI
    );

    constructor(address _treasury)
        ERC721("iCLONE Agent", "ICLONE")
        Ownable(msg.sender)
    {
        require(_treasury != address(0), "treasury=0");
        treasury = _treasury;
        _setDefaultRoyalty(_treasury, 500); // 5% secondary, ERC-2981
    }

    /// @notice Mint an agent. The merge of (image, soul, attributes) lives at `uri`.
    /// @param uri      tokenURI -> {image (on-chain SVG data URI), neural_soul, attributes}
    /// @param genome   deterministic provenance of the silhouette
    /// @param soulURI  Arweave URI of the base neural_soul.md
    function mintAgent(string calldata uri, Genome calldata genome, string calldata soulURI)
        external
        payable
        nonReentrant
        returns (uint256 id)
    {
        require(msg.value >= mintPrice, "insufficient ETH");
        require(bytes(soulURI).length != 0, "soul required");

        id = ++nextId;
        _safeMint(msg.sender, id);
        _setTokenURI(id, uri);
        genomeOf[id] = genome;
        soulOf[id]   = soulURI;

        (bool ok, ) = treasury.call{value: msg.value}("");
        require(ok, "treasury transfer failed");

        emit AgentMinted(id, msg.sender, genome, soulURI);
    }

    /// @notice The agent's controller. Off-chain runtime authenticates against this.
    function controllerOf(uint256 id) external view returns (address) {
        return ownerOf(id);
    }

    function setMintPrice(uint256 p) external onlyOwner { mintPrice = p; }

    function setTreasury(address t) external onlyOwner {
        require(t != address(0), "treasury=0");
        treasury = t;
    }

    function setDefaultRoyalty(address r, uint96 bps) external onlyOwner {
        _setDefaultRoyalty(r, bps);
    }

    function supportsInterface(bytes4 id_)
        public view override(ERC721URIStorage, ERC2981) returns (bool)
    {
        return super.supportsInterface(id_);
    }
}
