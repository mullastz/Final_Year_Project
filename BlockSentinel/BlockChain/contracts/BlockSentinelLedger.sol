// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract BlockSentinelLedger {
    struct TableRecord {
        string schemaName;
        string tableName;
        string[][] schema; // [["id", "integer"], ["name", "varchar"]]
        string[][] rows;   // [["1", "admin"], ["2", "user"]]
    }

    struct ActivityRecord {
        string activityType; // INSERT, UPDATE, DELETE
        string timestamp;
        string username;
        string query;
        string[][] newData;
    }

    // systemId => dbName => tableKey => TableRecord
    mapping(string => mapping(string => mapping(string => TableRecord))) private fullData;

    // systemId + tableKey => list of activity logs
    mapping(string => ActivityRecord[]) private activityLogs;

    /// Store full table data (initial extraction)
    function storeTableData(
        string memory systemId,
        string memory dbName,
        string memory tableKey,
        string memory schemaName,
        string memory tableName,
        string[][] memory schema,
        string[][] memory rows
    ) public {
        TableRecord storage record = fullData[systemId][dbName][tableKey];
        record.schemaName = schemaName;
        record.tableName = tableName;
        record.schema = schema;
        record.rows = rows;
    }

    /// Retrieve full table data
    function getTableData(
        string memory systemId,
        string memory dbName,
        string memory tableKey
    ) public view returns (
        string memory schemaName,
        string memory tableName,
        string[][] memory schema,
        string[][] memory rows
    ) {
        TableRecord storage record = fullData[systemId][dbName][tableKey];
        return (
            record.schemaName,
            record.tableName,
            record.schema,
            record.rows
        );
    }

    /// Store real-time activity
    function storeActivityLog(
        string memory systemId,
        string memory tableKey,
        string memory activityType,
        string memory timestamp,
        string memory username,
        string memory query,
        string[][] memory newData
    ) public {
        ActivityRecord memory log = ActivityRecord(
            activityType,
            timestamp,
            username,
            query,
            newData
        );

        string memory fullKey = string(abi.encodePacked(systemId, "_", tableKey));
        activityLogs[fullKey].push(log);
    }

    /// Retrieve all activity logs for a given system+table
    function getActivityLogs(string memory systemId, string memory tableKey)
        public view returns (ActivityRecord[] memory)
    {
        string memory fullKey = string(abi.encodePacked(systemId, "_", tableKey));
        return activityLogs[fullKey];
    }
}
