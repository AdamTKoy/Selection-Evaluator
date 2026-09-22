select 
  MES.model_entity_set_name as "synonym", 
  GROUP_CONCAT(M.modl_no, ', ') AS 'members' 
from cdms.model_entity_set MES
join cdms.entity_set_model_list ESML on MES.latest_modl_ent_ver_id = ESML.modl_entity_set_ver_id
join cdms.model M on ESML.modl_id = M.modl_id
  where MES.usage_stat_cd = 'A' and MES.obsolete_i = 0
group by
  MES.model_entity_set_name
order by
  MES.model_entity_set_name
;