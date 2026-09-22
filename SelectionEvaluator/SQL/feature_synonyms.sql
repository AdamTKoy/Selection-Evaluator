select
	FES.feature_entity_set_name as 'synonym',
	GROUP_CONCAT(F.fetr_no, ', ') AS 'members'
from cdms.feature_entity_set FES
join cdms.entity_set_feature_list ESFL
	on FES.latest_fetr_ent_ver_id = ESFL.fetr_entity_set_ver_id
join cdms.feature F on F.fetr_id = ESFL.fetr_id
join cdms.feature_group FG on FG.fetr_grp_id = F.fetr_grp_id
where
  FES.usage_stat_cd = 'A' and
  FES.obsolete_i = 0 and
  FES.feature_entity_set_name NOT LIKE "F-P-%" -- EXCLUDE NEW PARAMETER SYNONYMS FOR NOW
group by
	FES.feature_entity_set_name
order by
	FES.feature_entity_set_name
;