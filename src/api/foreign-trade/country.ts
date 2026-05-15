/**
 * 国家查询 API
 */
import request from '@/utils/http'

/** 搜索国家 */
export function fetchCountrySearch(q: string) {
  return request.get({ url: `/api/country/search`, params: { q } })
}

/** 获取国家详情 */
export function fetchCountryDetail(iso2: string) {
  return request.get({ url: `/api/country/${iso2}` })
}

/** 获取城市列表 */
export function fetchCountryCities(iso2: string) {
  return request.get({ url: `/api/country/${iso2}/cities` })
}

/** 邮编查询 */
export function fetchPostalLookup(iso2: string, postalCode: string) {
  return request.get({ url: `/api/country/${iso2}/postal/${postalCode}` })
}

/** 获取地区列表 */
export function fetchCountryRegions() {
  return request.get({ url: `/api/country/regions` })
}

/** 获取所有国家 */
export function fetchAllCountries() {
  return request.get({ url: `/api/country/all` })
}
