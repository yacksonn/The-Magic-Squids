-- Refresh data to be cleaned and integrated
SELECT * FROM trr_trr_refresh;
SELECT * FROM trr_actionresponse_refresh;
SELECT * FROM trr_charge_refresh;
SELECT * FROM trr_subjectweapon_refresh;
SELECT * FROM trr_trrstatus_refresh;
SELECT * FROM trr_weapondischarge_refresh;


-- Data needed to check values against for reconciliation
SELECT * FROM trr_trr;
SELECT * FROM trr_actionresponse;
SELECT * FROM trr_charge;
SELECT * FROM trr_subjectweapon;
SELECT * FROM trr_trrstatus;
SELECT * FROM trr_weapondischarge;
SELECT * FROM data_officer;
SELECT * FROM data_policeunit;