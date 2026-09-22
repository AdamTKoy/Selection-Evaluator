select 
  FG.fetr_grp_no as "FG",
  F.fetr_no as "feature"
from feature F
join feature_group FG on FG.fetr_grp_id = F.fetr_grp_id
  where F.usage_stat_cd = 'A'
  and F.obsolete_i = 0
order by 
  FG.fetr_grp_no, 
  F.fetr_no
;