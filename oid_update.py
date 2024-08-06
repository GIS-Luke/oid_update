""" OIDupdate.py exists because esri software can not make views of tables which
 do not have an OBJECTID field. It can be done via SQL if you have the access
 This script truncates esri tables and appends the rows from SSIS tables so
 that the esri tables can participate in spatial views.
 Registering with the geodatabase would have the same effect, however
 the source tables are recreated overnight.
 Updating the records in registered table was the better workflow.
 20220504 edited to include truncate and append from dbvw to fc that must
 occure after OID update.
 20230221 Added Path Animal register block
 20240805 Truncate removal, sendErrorEmail removal
 and adding 'gis.gisdba.' update.
"""
import arcpy as ap

gis = r'\\cappgis10\d$\ArcGISCatalog\SDEConnections\cdbpsql20GISgisdba.sde'
gg = 'gis.gisdba.'
ap.env.workspace = gis

# update the following in ALPHABETICAL ORDER
# last updated 20240411 
tbls = [u'ExportFromPathway_Bins',
        u'ExportFromPATHWAY_CI_AP_APPS',
        u'ExportFromPATHWAY_CI_OHP_APPS',
        u'ExportFromPATHWAY_CI_VC_APPS',
        u'ExportFromPathwayAllApplicationsLicenses', 
        u'ExportFromPathwayAllCRS_VHTMQuestions',  
        u'ExportFromPathwayAnimals_Active',
        u'ExportFromPathwayAnimals_Unregistered',
        u'ExportFromPathwayBldEnforcement',
        u'ExportFromPathwayCarShare',
        u'ExportFromPathwayCommunityManagedNatureStrip',
        u'ExportFromPathwayDimensions',
        u'ExportFromPathwayInspections',
        u'ExportFromPathwayLicensing',
        u'ExportFromPathwayLICs',  
        u'ExportFromPATHWAYNOSPRAY', 
        u'ExportFromPathwayParentProps',
        u'ExportFromPathwayPlanning',
        u'ExportFromPathwayPlanning_Questions',
        u'ExportFromPATHWAYPOOLS', 
        u'ExportFromPathwayPopUps',
        u'ExportFromPathwayPropertyOwnershipLanduse',
        u'ExportFromPathwayRateCodesWasteServices',
        u'ExportFromPathwayRateTypes',
        u'ExportFromPathwayRdClosureOpening_V2',
        u'ExportFromPathwayRdClosureOpening_V2_Applicants',
        u'ExportFromPathwayRdClosureOpening_V2_Questions',
        u'ExportFromPATHWAYSUBDIVISIONCERTIFICATIONS']

terms = ("'https://www.merri-bek.vic.gov.au/building-and-business'"
         "'/planning-and-building/strategic-planning'"
         "'/moreland-planning-scheme/#autoAnchor4'")
disclaimer = ("'The associated documents (if listed) have been scanned '"
              "'and made available for the purpose of the planning process '"
              "'as set out in the Planning and Environment Act 1987. '"
              "'The information must not be used for any other purpose. '"
              "'By opening a copy of these documents you acknowledge and '"
              "'agree that you will only use the documents for the purpose '"
              "'specified above and that any dissemination, distribution '"
              "'or copying of these documents is strictly prohibited. '"
              "'If you have any questions, please contact Council '"
              "'on 9240 1111.'")
docs_expression = ("'https://eservicesdoc.moreland.vic.gov.au'"
                   "'/kapishwebgrid/default.aspx?s=eServices&container=' + "
                   "!Formatted_Application_Number!")
terms_field = 'Planning_Terms'
disc_field = 'Document_Disclaimer'
docs_field = 'Assoc_Documents'

for tbl in tbls:
    gg_tbl_1 = gg + tbl + '_1'
    ap.DeleteRows_management(gg_tbl_1)
    gg_tbl = gg + tbl
    ap.Append_management(gg_tbl, gg_tbl_1, 'NO_TEST')
    if tbl == 'ExportFromPathwayPlanning':
        ap.CalculateField_management(gg_tbl_1,
                                     terms_field,
                                     terms,
                                     'PYTHON3')
        ap.CalculateField_management(gg_tbl_1,
                                     disc_field,
                                     disclaimer,
                                     'PYTHON3')
        ap.CalculateField_management(gg_tbl_1,
                                     docs_field,
                                     docs_expression,
                                     'PYTHON3')
# Next block added upon request by GIS Coordinator
active = gg + 'ExportfromPathwayAnimals_Active_1'
unregistered = gg + 'ExportfromPathwayAnimals_Unregistered_1'
combined = gg + 'ExportfromPathwayAnimals_ActiveUnregCombined'
#ap.TruncateTable_management(combined)
ap.DeleteRows_management(combined)
ap.Append_management(active,
                     combined,
                     'NO_TEST')
ap.CalculateField_management(combined,
                             'Source',
                             '"Animals_Active"',#ap sql quote quirk
                             'PYTHON3')
ap.Append_management(unregistered,
                     combined,
                     'NO_TEST')
unreg = 'unregistered'
# ALL SQL or FIELD NAME so only one set of quotes needed
# since no strings
animal_where = 'Source IS NULL'
ap.MakeTableView_management(combined,
                            unreg,
                            animal_where)
ap.CalculateField_management(unreg,
                             'Source',
                             '"Animals_Unregistered"',
                             'PYTHON3')
# Another block requested by coordinator
fc = gg + 'DbVw_PthWy_Animals_RegUnreg_PtsHistUniq_AllRecords_MappedAndUnmapped_fc'
fcs = [gg + 'DbVw_PthWy_Animals_RegUnreg_PtsHistUniq_AllRecords',
       gg + 'DbVw_PthWy_Animals_RegUnreg_PtsHistUniq_AllRecords_NonMapping']
ap.DeleteRows_management(fc)
ap.Append_management(fcs,
                     fc,
                     'NO_TEST')
