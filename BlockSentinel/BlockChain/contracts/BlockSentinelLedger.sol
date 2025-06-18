// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BlockSentinelLedger {
    struct TableRecord {
        string schemaName;
        string tableName;
        string[][] schema;
        string[][] rows;
    }

    struct LedgerMeta {
        string dbName;
        string batchId;
        string timestamp;
    }

    // Stores full table data
    mapping(string => mapping(string => mapping(string => TableRecord))) private fullData;

    // Stores table metadata for recovery
    mapping(string => string[]) private systemToTableKeys;             // systemId => list of tableKeys
    mapping(string => LedgerMeta) private ledgerMetadata;             // systemId.tableKey => metadata

    // 🔐 Store both full data and metadata
    function storeTableData(
        string memory systemId,
        string memory dbName,
        string memory tableKey,
        string memory schemaName,
        string memory tableName,
        string[][] memory schema,
        string[][] memory rows,
        string memory batchId,
        string memory timestamp
    ) public {
        // Save the full table snapshot
        TableRecord storage record = fullData[systemId][dbName][tableKey];
        record.schemaName = schemaName;
        record.tableName = tableName;
        record.schema = schema;
        record.rows = rows;

        // Save metadata for ledger index
        string memory fullKey = string(abi.encodePacked(systemId, ".", tableKey));
        ledgerMetadata[fullKey] = LedgerMeta(dbName, batchId, timestamp);

        // Track tableKey under this system if not already added
        bool exists = false;
        for (uint i = 0; i < systemToTableKeys[systemId].length; i++) {
            if (keccak256(bytes(systemToTableKeys[systemId][i])) == keccak256(bytes(tableKey))) {
                exists = true;
                break;
            }
        }
        if (!exists) {
            systemToTableKeys[systemId].push(tableKey);
        }
    }

    // 📖 View full table snapshot
    function getTableData(string memory systemId, string memory dbName, string memory tableKey)
        public
        view
        returns (
            string memory schemaName,
            string memory tableName,
            string[][] memory schema,
            string[][] memory rows
        )
    {
        TableRecord storage record = fullData[systemId][dbName][tableKey];
        return (
            record.schemaName,
            record.tableName,
            record.schema,
            record.rows
        );
    }

    // 📖 View table keys for a system (used to rebuild ledger index)
    function getSystemTableKeys(string memory systemId)
        public
        view
        returns (string[] memory)
    {
        return systemToTableKeys[systemId];
    }

    // 📖 View metadata for a table
    function getLedgerMetadata(string memory systemId, string memory tableKey)
        public
        view
        returns (
            string memory dbName,
            string memory batchId,
            string memory timestamp
        )
    {
        string memory fullKey = string(abi.encodePacked(systemId, ".", tableKey));
        LedgerMeta storage meta = ledgerMetadata[fullKey];
        return (meta.dbName, meta.batchId, meta.timestamp);
    }
}
