import datetime
import azure.functions as func
import azure.functions as func
from azure.cosmosdb.table.models import Entity
from azure.cosmosdb.table.tablebatch import TableBatch
from azure.cosmosdb.table.tableservice import TableService
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


# from azure.mgmt.keyvault import KeyVaultManagementClient
# from azure.common.credentials import ServicePrincipalCredentials


from .earthquakedata import *


def main(mytimer: func.TimerRequest) -> None:
    # def main():
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    access_token = getSecret()
    print(access_token)
    private_key_raw = getMultiplsecrets(
        "guprodadobekeys", "adobeApi", "6dfaa779342b434c82a7053db36f6303", access_token
    )

    key_formated = private_key_raw.replace(" ", "\n")
    private_key = "-----BEGIN PRIVATE KEY-----\n{}\n-----END PRIVATE KEY-----".format(
        key_formated
    )
    table_key = getMultiplsecrets(
        "guprodadobekeys",
        "guwebanalyticskey",
        version_id,
        access_token,
    )
    account_name = "guwebanalyticsprd"
    hourly_data = earthquakes_location()
    formatted_quakelocation, formatted_quakedetails = populate_dict(hourly_data)
    quake_locations_table_name = "details"
    quake_details_table_name = "locations"
    db_name = "earthquake.db"
    dict_to_table(formatted_quakedetails, quake_details_table_name, db_name)
    dict_to_table(formatted_quakelocation, quake_locations_table_name, db_name)
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)


# if __name__ == "__main__":
#     main()
