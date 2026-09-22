select 
  MMAC.modl_no as "model",
  FG.fetr_grp_no as "fg",
  MMAC.fetr_no as "feature"
from cdms.mmacfeature MMAC
join cdms.model M on MMAC.modl_no = M.modl_no
join cdms.feature F on MMAC.fetr_no = F.fetr_no
join cdms.feature_group FG on F.fetr_grp_id = FG.fetr_grp_id
  where M.usage_stat_cd = "A"
  and M.obsolete_i = 0
  and F.usage_stat_cd = 'A'
  and F.obsolete_i = 0
  and MMAC.in_mktg_dte is not null
  and 
  (
  cast(MMAC.out_mktg_dte as date) >= CURRENT_DATE()
  or
  MMAC.out_mktg_dte is null
  )
group by
  MMAC.modl_no,
  FG.fetr_grp_no,
  MMAC.fetr_no
order by
  MMAC.modl_no,
  FG.fetr_grp_no,
  MMAC.fetr_no
;