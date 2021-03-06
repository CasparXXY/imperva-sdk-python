###########################################################################################################
#
# This unittest runs a basic sanity for imperva_sdk that should ensure most things are working properly -
# 1) Create resources
# 2) Export to JSON
# 3) Delete resources
# 4) Import from JSON
# 5) Get resources
#
# You need to set the MX information by system variables - 
# MX_HOST, MX_PASSWORD, MX_USER & MX_PORT
#
# You may also set MX_LICENSE with the location of a license file for the api to load into the MX
#
###########################################################################################################

import unittest
import imperva_sdk
import os

class TestImpervaSdkSanity(unittest.TestCase):

  host			= None
  user			= "admin"
  password		= "password"
  port			= 8083
  license		= ""

  test_action_set	= True
  test_http_protocol_signatures_policy	= True
  test_parameter_type_global_object	= True
  test_profile		= True
  test_web_profile_policy = True

  test_db_connection = True
  test_assessment_scan = True
  test_classification_scan = True
  test_db_audit_policy = True
  test_db_audit_report = True

  Site			= {"Name": "imperva_sdk sanity site"}
  ServerGroup		= {"Name": "imperva_sdk sanity server group", "Site": Site["Name"], "ProtectedIps": [], "OperationMode": "active", "ServerIps": ["1.1.1.1"]}
  WebService		= {"Name": "imperva_sdk sanity web service", "ServerGroup": ServerGroup["Name"], "Site": Site["Name"]}
  WebApplication	= {"Name": "imperva_sdk sanity web application", "WebService": WebService["Name"], "ServerGroup": ServerGroup["Name"], "Site": Site["Name"], "Mappings": [{ "priority": 1, "host": "www.myapp.com", "hostMatchType": "Exact" }]}
  DbService = {"Name": "imperva_sdk sanity db service", "ServerGroup": ServerGroup["Name"], "Site": Site["Name"], "DbServiceType": "Oracle"}

  ActionSet		= {"Name": "imperva_sdk sanity action set", "AsType": "security"}
  Action		= {
                            "Name": "imperva_sdk sanity action", 
                            "ActionType": "GWSyslog", 
                            "Port": "514", 
                            "Host": "syslog-server", 
                            "Protocol": "TCP", 
                            "SyslogLogLevel": "DEBUG", 
                            "SyslogFacility": "LOCAL0", 
                            "ActionInterface": "Gateway Log - Security Event - System Log (syslog) - JSON format (Extended)"
                          }

  WebServiceCustomPolicy = {
                            "Name": "imperva_sdk sanity web service custom policy",
                            "MatchCriteria": [{ "type": "httpRequestUrl", "operation": "excludeAll", "values": ["/login"], "match": "exact" }],
                            "ApplyTo": [{'siteName': Site["Name"], 'serverGroupName': ServerGroup["Name"], 'webServiceName': WebService["Name"]}],
                            "FollowedAction": ActionSet["Name"],
                            "Enabled": True,
                            "OneAlertPerSession": True,
                            "DisplayResponsePage": True,
                            "Action": "block",
                            "SendToCd": None,
                            "Severity": "high"
                          }

  ParameterTypeGlobalObject = {
				"Name": "imperva_sdk sanity parameter type configuration",
				"Regex": ".*"
			}

  HttpProtocolSignaturesPolicy = {
                            "Name": "imperva_sdk sanity http protocol signatures policy", 
                            "ApplyTo": [{'siteName': Site["Name"], 'serverGroupName': ServerGroup["Name"], 'webServiceName': WebService["Name"]}],
                            "Rules": [{u'action': u'block', u'enabled': True, u'name': u'Recommended for Blocking for Web Applications ', u'severity': u'medium', 'followedAction': ActionSet["Name"]}], 
                            "Exceptions": [{u'comment': u'exception comment', u'predicates': [{u'type': u'httpRequestUrl', u'operation': u'atLeastOne', u'values': [u'/login', '/logout'], u'match': u'prefix'}], u'ruleName': u'Recommended for Blocking for Web Applications '}]
                          }

  WebProfilePolicy = {
    "Name": "imperva_sdk sanity web profile policy",
    "ApplyTo": [{'siteName': Site["Name"], 'serverGroupName': ServerGroup["Name"], 'webServiceName': WebApplication["WebService"], 'webApplicationName': WebApplication['Name']}],
    "Rules": [{'name': 'Cookie Injection', 'enabled': True, 'severity': 'medium', 'action': 'none'}],
    "Exceptions": [{'ruleName': 'Cookie Injection', 'comment': 'Sanity Exception', 'predicates': [{'matchNoOrUnknownUser': False, 'values': ['Sanity'], 'type': 'applicationUser', 'operation': 'atLeastOne'}]}],
    "ApuConfig": {'SOAP Element Value Length Violation': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'Parameter Read Only Violation': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, "Reuse of Expired Session's Cookie": {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'SOAP Element Value Type Violation': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'Required Parameter Not Found': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'Unauthorized Method for Known URL': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'Unknown Parameter': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'Parameter Type Violation': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'Unauthorized SOAP Action': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'Unknown SOAP Element': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'Required XML Element Not Found': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'Parameter Value Length Violation': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'Cookie Injection': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}, 'Cookie Tampering': {'enabled': True, 'sources': 50, 'occurrences': 50, 'hours': 12}},
    "DisableLearning": False,
    "DisplayResponsePage": True
  }

  Swagger		= {
                            "swagger": "2.0",
                            "info": { "version": "1.0", "title": "GioraHack-serverless-todo" },
                            "host": "www.myapp.com",
                            "basePath": "/Prod",
                            "schemes": [ "https" ],
                            "paths": {
                              "/todos": { "get": { "responses": {} }, "post": { "responses": {} } },
                              "/todos/{id}": { "put": { "responses": {} } }
                            }
                          }

  DbConnection = {
    "SiteName": Site["Name"],
    "ServerGroupName": ServerGroup["Name"],
    "ServiceName": DbService["Name"],
    "ConnectionName" : "imperva_sdk sanity db connection",
    "IpAddress": ServerGroup["ServerIps"][0],
    "UserName": "system",
    "Password": "123456",
    "DbName": "orcl",
    "Port": "1521",
  }

  AssessmentScan = {
    "Name": "imperva_sdk sanity assessment scan",
    "Type": "policy based",
    "PolicyName": "Oracle Known Vulnerabilities",
    "ApplyTo":["conf/dbServices/" + Site["Name"] + "/" + ServerGroup["Name"] + "/" + DbService["Name"] + "/dbConnections/" + DbConnection["ConnectionName"]]
  }

  ClassificationProfile = {
    "Name": "imperva_sdk sanity classification profile",
    "SiteName": Site["Name"],
    "DataTypes": ["Password", "Phone", "ZIP Code"],
    "AutoAcceptResults": "true",
    "ScanViewsAndSynonyms": "true",
    "SaveSampleData": "false",
    "ScanSystemSchemas": "false",
    "DataSampleAccuracy": "0.75",
    "DbsAndSchemasUsage": "include",
    "DbsAndSchemas": [{"database": "db1", "schema": "any"}],
    "ExcludeTablesAndColumns": [{"table": "any", "column": "column1"}]
  }

  ClassificationScan = {
    "Name": "imperva_sdk sanity classification scan",
    "ProfileName": ClassificationProfile["Name"],
    "ApplyTo": ["conf/dbServices/" + Site["Name"] + "/" + ServerGroup["Name"] + "/" + DbService["Name"] + "/dbConnections/" + DbConnection["ConnectionName"]]
  }

  DbAuditPolicy = {
    "aggregation-time-slot": "30",
    "num-days-to-audit": "7",
    "counterbreach-policy-enabled": "false",
    "user-defined-values": [],
    "collect-statistics": "true",
    "audit-responses-mode":	"All",
    "data-collection-events": "true",
    "use-gateway-configuration": "false",
    "policy-name": "imperva_sdk sanity db audit policy",
    "purge-archive-scheduling": {"enabled": "true", "number": "1", "time-type": "weeks"},
    "archiving-action-set": "Default Archive Action Set",
    "archive-scheduling": {"occurs": "none"},
    "audit-parsed-query": "true",
    "automatic-apply": "NotSet",
    "archive-response": "false",
    "quota-giga-bytes": "200",
    "policy-type": "db-service",
    "apply-to": [],
    "data-collection-db-response": "false",
    "quota-percentage": "50",
    "match-criteria": [
      {"values": [{"value": "select"}], "operation": "At least one", "type": "simple", "name": "Operations Tables", "handle-unknown-values": "false"},
      {"sql-groups": [{"name": "Classified Objects"}], "name": "Table Groups", "values": [], "handle-unknown-values": "false", "operation": "At least one", "type": "table-group"}
    ]
  }

  DbAuditReport = {
    "Columns": [{"name": "Database", "aggregation": "count-distinct"},{"name": "Service", "aggregation": "group-by-id-name-of-service-id-name"},{"name": "Destination IP", "aggregation": "group-by"}],
    "Filters": [{"values": ["5593158133644499881"], "column-name": "Server Group", "operation": "equals", "user-defined-values": []}],
    "Policies": [DbAuditPolicy["policy-name"]],
    "Sorting": [{"aggregation": "group-by-id-name-of-service-id-name", "direction": "asc", "column-name": "Service"}],
    "Name": "imperva_sdk sanity db audit report",
    "ReportFormat": "pdf",
    "TimeFrame": {"from-to": "true", "from-date": 1533070800000, "to-date": 1535317200000},
    "Scheduling": {"occurs": "recurring", "recurring": {"frequency": "daily", "daily": { "every-number-of-days": 1}, "starting-from": "2018-08-29", "at-time": "00:00:00"}
    }
}


  def setUp(self):
    if 'MX_HOST' in os.environ: self.host = os.environ['MX_HOST']
    if 'MX_USER' in os.environ: self.user = os.environ['MX_USER']
    if 'MX_PASSWORD' in os.environ: self.password = os.environ['MX_PASSWORD']
    if 'MX_PORT' in os.environ: self.port = int(os.environ['MX_PORT'])
    if 'MX_LICENSE' in os.environ: self.license = os.environ['MX_LICENSE']
    if not self.host:
      raise Exception("No MX specified (MX_HOST environment variable)")

  def tearDown(self):
    pass

  def test_sdk_license(self):
    # Try to upload a license if it is provided
    if self.license:
      mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port, FirstTime=True)
      try:
        mx.upload_license(LicenseFile=self.license)
      except imperva_sdk.MxException as e:
        if 'IMP-12107' in e.args[0]:
          pass
        else:
          raise e
      mx.logout

  def test_waf_sdk_sanity(self):

    # Try to upload a license if it is provided
    if self.license:
      mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port, FirstTime=True)
      try:
        mx.upload_license(LicenseFile=self.license)
      except imperva_sdk.MxException as e:
        if 'IMP-12107' in e.args[0]:
          pass
        else:
          raise e
      mx.logout

    # Delete test resources if they exist from previous runs
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    if mx.get_site(self.Site["Name"]): mx.delete_site(self.Site["Name"])
    if mx.get_http_protocol_signatures_policy(self.HttpProtocolSignaturesPolicy["Name"]): mx.delete_http_protocol_signatures_policy(self.HttpProtocolSignaturesPolicy["Name"])
    if mx.get_parameter_type_global_object(self.ParameterTypeGlobalObject["Name"]): mx.delete_parameter_type_global_object(self.ParameterTypeGlobalObject["Name"])
    if mx.get_web_service_custom_policy(self.WebServiceCustomPolicy["Name"]): mx.delete_web_service_custom_policy(self.WebServiceCustomPolicy["Name"])
    if mx.get_action_set(self.ActionSet["Name"]): mx.delete_action_set(self.ActionSet["Name"])
    if mx.get_web_profile_policy(self.WebProfilePolicy['Name']): mx.delete_web_profile_policy(self.WebProfilePolicy['Name'])
    mx.logout()

    # Create test resources
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    mx.create_site(**self.Site)
    mx.create_server_group(**self.ServerGroup)
    mx.create_web_service(**self.WebService)
    app = mx.create_web_application(**self.WebApplication)
    try:
      mx.create_action_set(**self.ActionSet)
      mx.create_action(ActionSet=self.ActionSet["Name"], **self.Action)
    except imperva_sdk.MxExceptionNotFound:
      self.test_action_set = False
      self.WebServiceCustomPolicy["FollowedAction"] = "Long IP Block"
      self.HttpProtocolSignaturesPolicy["Rules"][0]["followedAction"] = "Long IP Block"
    try:
      mx.create_http_protocol_signatures_policy(**self.HttpProtocolSignaturesPolicy)
    except imperva_sdk.MxExceptionNotFound:
      self.test_http_protocol_signatures_policy = False
    try:
      mx.create_parameter_type_global_object(**self.ParameterTypeGlobalObject)
    except imperva_sdk.MxExceptionNotFound:
      self.test_parameter_type_global_object = False
    try:
      app.update_profile(SwaggerJson=self.Swagger)
    except imperva_sdk.MxExceptionNotFound:
      self.test_profile = False
    mx.create_web_service_custom_policy(**self.WebServiceCustomPolicy)
    try:
      mx.create_web_profile_policy(**self.WebProfilePolicy)
    except imperva_sdk.MxExceptionNotFound:
      self.test_web_profile_policy = False
    mx.logout()

    # Export to JSON
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    export = mx.export_to_json()
    mx.logout()

    # Delete test resources
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    mx.delete_web_application(self.WebApplication["Name"], WebService=self.WebService["Name"], ServerGroup=self.ServerGroup["Name"], Site=self.Site["Name"])
    mx.delete_web_service(**self.WebService)
    mx.delete_server_group(self.ServerGroup["Name"], Site=self.Site["Name"])
    if self.test_http_protocol_signatures_policy:
      mx.delete_http_protocol_signatures_policy(self.HttpProtocolSignaturesPolicy["Name"])
    if self.test_parameter_type_global_object:
      mx.delete_parameter_type_global_object(self.ParameterTypeGlobalObject["Name"])
    mx.delete_web_service_custom_policy(self.WebServiceCustomPolicy["Name"])
    if self.test_web_profile_policy:
      mx.delete_web_profile_policy(self.WebProfilePolicy['Name'])
    mx.delete_site(**self.Site)
    if self.test_action_set:
      mx.delete_action(ActionSet=self.ActionSet["Name"], Name=self.Action["Name"])
      mx.delete_action_set(self.ActionSet["Name"])
    mx.logout()

    # Import from JSON
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    log = mx.import_from_json(export)
    for entry in log:
      if entry["Result"] != "SUCCESS":
        raise Exception("import_from_json failure - %s" % str(entry))
    mx.logout()

    # Get test resources
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    site = mx.get_site(**self.Site)
    if not site: raise Exception("Failed getting site")
    server_group = mx.get_server_group(self.ServerGroup["Name"], Site=self.Site["Name"])
    if server_group.OperationMode != self.ServerGroup["OperationMode"]: raise Exception("Failed getting server group properties")
    web_service = mx.get_web_service(**self.WebService)
    if not web_service: raise Exception("Failed getting web service")
    web_application = mx.get_web_application(self.WebApplication["Name"], WebService=self.WebService["Name"], ServerGroup=self.ServerGroup["Name"], Site=self.Site["Name"])
    if not web_application.Mappings[0]["host"] == self.WebApplication["Mappings"][0]["host"]: raise Exception("Failed getting web application properties")
    if self.test_action_set:
      action = mx.get_action(self.Action["Name"], ActionSet=self.ActionSet["Name"])
      if not action.ActionInterface == self.Action["ActionInterface"]: raise Exception("Failed getting action properties")
    if self.test_http_protocol_signatures_policy:
      pol = mx.get_http_protocol_signatures_policy(self.HttpProtocolSignaturesPolicy["Name"])
      if pol.Rules[0]["action"] != self.HttpProtocolSignaturesPolicy["Rules"][0]["action"]: raise Exception("Failed getting http protocol signatures policy properties")
    if self.test_parameter_type_global_object:
      obj = mx.get_parameter_type_global_object(self.ParameterTypeGlobalObject["Name"])
      if obj.Regex != self.ParameterTypeGlobalObject["Regex"]: raise Exception("Failed getting parameter type configuration global object")
    if self.test_profile:
      profile = web_application.get_profile()
      if len(profile["webProfileUrls"]) != len(self.Swagger["paths"]): raise Exception("Failed getting profile")
    pol = mx.get_web_service_custom_policy(self.WebServiceCustomPolicy["Name"])
    if pol.FollowedAction != self.WebServiceCustomPolicy["FollowedAction"]: raise Exception("Failed getting web service custom policy")
    if self.test_web_profile_policy:
      policy = mx.get_web_profile_policy(self.WebProfilePolicy['Name'])
      if not policy:
        raise Exception("Failed getting WebProfilePolicy %s" % self.WebProfilePolicy['Name'])
    mx.logout()

  def test_dam_das_sdk_sanity(self):

    # Delete test resources if they exist from previous runs
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    if mx.get_site(self.Site["Name"]):
      mx.delete_site(self.Site["Name"])
    if mx.get_assessment_scan(self.AssessmentScan["Name"]):
      mx.delete_assessment_scan(self.AssessmentScan["Name"])
    if mx.get_classification_scan(self.ClassificationScan["Name"]):
      mx.delete_classification_scan(self.ClassificationScan["Name"])
    if mx.get_classification_profile(self.ClassificationProfile["Name"]):
      mx.delete_classification_profile(self.ClassificationProfile["Name"])
    if mx.get_db_audit_policy(self.DbAuditPolicy["policy-name"]):
      mx.delete_db_audit_policy(self.DbAuditPolicy["policy-name"])
    #if mx.get_db_audit_report(self.DbAuditReport["display-name"]):
      # delete_db_audit_report is not implemented
    #if mx.get_db_connection(self.Site["Name"], self.ServerGroup["Name"], self.DbService["Name"], selfDbConnection["ConnectionName]):
      # delete_db_connection is not implemented correctly
    mx.logout()

    # Create test resources
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    mx.create_site(**self.Site)
    mx.create_server_group(**self.ServerGroup)
    mx.create_db_service(**self.DbService)
    try:
      mx.create_db_connection(**self.DbConnection)
    except imperva_sdk.MxExceptionNotFound:
      self.test_db_connection = False
    try:
      mx.create_assessment_scan_das_object(**self.AssessmentScan)
    except imperva_sdk.MxExceptionNotFound:
      self.test_assessment_scan = False
    try:
      mx.create_classification_profile(**self.ClassificationProfile)
      mx.create_classification_scan_das_object(**self.ClassificationScan)
    except imperva_sdk.MxExceptionNotFound:
      self.test_classification_scan = False
    try:
      mx.create_db_audit_dam_policy(Name=self.DbAuditPolicy["policy-name"], Parameters=self.DbAuditPolicy)
    except imperva_sdk.MxExceptionNotFound:
      self.test_db_audit_policy = False
    # try:
    #   mx.create_db_audit_dam_report(Name=self.DbAuditReport["Name"], ReportFormat=self.DbAuditReport["ReportFormat"], Columns=self.DbAuditReport["Columns"],
    #                                 Filters=self.DbAuditReport["Filters"], Policies=self.DbAuditReport["Policies"], Sorting=self.DbAuditReport["Sorting"],
    #                                 TimeFrame=self.DbAuditReport["TimeFrame"], Scheduling=self.DbAuditReport["Scheduling"])
    # except imperva_sdk.MxExceptionNotFound:
    #   self.test_db_audit_Report = False
    mx.logout()

    # Export to JSON
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    export = mx.export_to_json()
    mx.logout()

    # Delete test resources
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    if mx.get_site(self.Site["Name"]):
      mx.delete_site(self.Site["Name"])
    if mx.get_assessment_scan(self.AssessmentScan["Name"]):
      mx.delete_assessment_scan(self.AssessmentScan["Name"])
    if mx.get_classification_scan(self.ClassificationScan["Name"]):
      mx.delete_classification_scan(self.ClassificationScan["Name"])
    if mx.get_classification_profile(self.ClassificationProfile["Name"]):
      mx.delete_classification_profile(self.ClassificationProfile["Name"])
    if mx.get_db_audit_policy(self.DbAuditPolicy["policy-name"]):
      mx.delete_db_audit_policy(self.DbAuditPolicy["policy-name"])
    #if mx.get_db_audit_report(self.DbAuditReport["display-name"]):
      # delete_db_audit_report is not implemented
    #if mx.get_db_connection(self.Site["Name"], self.ServerGroup["Name"], self.DbService["Name"], selfDbConnection["ConnectionName]):
      # delete_db_connection is not implemented correctly
    mx.logout()

    # Import from JSON
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    log = mx.import_from_json(export)
    for entry in log:
      if entry["Result"] != "SUCCESS":
        raise Exception("import_from_json failure - %s" % str(entry))
    mx.logout()

    # Get test resources
    mx = imperva_sdk.MxConnection(Host=self.host, Username=self.user, Password=self.password, Port=self.port)
    site = mx.get_site(**self.Site)
    if not site: raise Exception("Failed getting site")
    server_group = mx.get_server_group(self.ServerGroup["Name"], Site=self.Site["Name"])
    if server_group.OperationMode != self.ServerGroup["OperationMode"]: raise Exception(
        "Failed getting server group properties")
    db_service = mx.get_db_service(Name=self.DbService["Name"], Site=self.DbService["Site"], ServerGroup=self.DbService["ServerGroup"])
    if not db_service: raise Exception("Failed getting web service")
    if self.test_assessment_scan:
      assess_scan = mx.get_assessment_scan(Name=self.AssessmentScan["Name"])
      if assess_scan.Type != self.AssessmentScan["Type"]: raise Exception("imported assessment scan is different from the exported scan")
    if self.test_classification_scan:
      classification_scan = mx.get_classification_scan(Name=self.ClassificationScan["Name"])
      classification_profile = mx.get_classification_profile(classification_scan.ProfileName)
      if str(classification_profile.Name) != str(self.ClassificationProfile["Name"]): raise Exception("imported classification profile is different from the exported profile")
    #get_db_audit_policy is not implemented correctly
    # if self.test_db_audit_policy:
    #   audit_policy = mx.get_db_audit_policy(self.DbAuditPolicy["policy-name"])
    #   if audit_policy is None: raise Exception("could not retrieve imported db audit policy")
    # if self.test_db_audit_report:
    #   audit_report = mx.get_db_audit_report(self.DbAuditReport["Name"])
    #   if audit_report is None: raise Exception("could not retrieve imported db audit report")

if __name__ == '__main__':

  suite = unittest.TestLoader().loadTestsFromTestCase(TestImpervaSdkSanity)
  unittest.TextTestRunner(verbosity=2).run(suite)
