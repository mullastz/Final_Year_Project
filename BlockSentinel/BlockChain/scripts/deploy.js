const hre = require("hardhat");

async function main() {
  const Ledger = await hre.ethers.getContractFactory("BlockSentinelLedger");
  const ledger = await Ledger.deploy();

  await ledger.waitForDeployment(); // ✅ ethers v6 method

  console.log("✅ Contract deployed to:", await ledger.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
