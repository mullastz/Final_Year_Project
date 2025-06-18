const hre = require("hardhat");

async function main() {
  // Get the contract factory
  const Ledger = await hre.ethers.getContractFactory("BlockSentinelLedger");

  // Deploy the contract
  const ledger = await Ledger.deploy();

  // Wait for the deployment to be mined
  await ledger.waitForDeployment();

  // Log the deployed contract address
  console.log("✅ Contract deployed to:", await ledger.getAddress());
}

// Run the deployment and catch errors
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
