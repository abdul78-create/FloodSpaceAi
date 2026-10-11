# FloodSpaceAI स्थिति प्रतिवेदन — Run `trishuli_benchmark_verified`

**घटना मिति:** `2026-08-28`  
**विश्लेषण क्षेत्र (AOI):** `[84.9, 27.75, 85.25, 28.05]`  
**OpenStreetMap स्न्यापसट मिति:** `2026-07-27T00:00:00Z`  
**डेटा मोड:** `VERIFIED_TRISHULI_BENCHMARK_CACHE`  
**उत्पादन समय:** `2026-10-09T15:34:09.352657+00:00`

---

## १. अवस्थाको संक्षिप्त विवरण
FloodSpaceAI ले Copernicus Sentinel उपग्रह डेटा र पूर्व-बाढी OpenStreetMap पूर्वाधारको प्रयोग गरेर बाढी अवस्थाको विश्लेषण गरेको छ।

- सम्भावित बाढी पिक्सेल: **1,286**
- सम्भावित बाढी क्षेत्र: **35.03 ha**
- सम्भावित प्रभावित भवन: **195** (एक्सपोजर ओभरले)
- सम्भावित प्रभावित सडक: **115** (59.26 km)
- सम्भावित प्रभावित पुल: **13**
- सम्भावित रूपमा सडक सम्पर्कबाट छुटेका बस्ती: **18**

> **वैज्ञानिक सूचना:** यी तथ्याङ्कहरू मोडेल गरिएका सम्भावित बाढी क्षेत्र र सडक सञ्जाल विच्छेदमा आधारित हुन्। वास्तविक भौतिक क्षति वा पूर्ण अलगावको पुष्टि गरिएको होइन।

---

## २. उपग्रह अवलोकन र कभरेज
- **SAR सेन्सर:** Sentinel-1 C-band synthetic aperture radar (सबै मौसममा अवलोकन गर्न सकिने)।
- **अप्टिकल सेन्सर:** Sentinel-2 multispectral MSI (Scene Classification Layer बादल मास्किङ गरिएको)।
- **अप्टिकल कभरेज अवस्था:** Generated 1,286 candidate pixels across 27 clusters.।
- **व्याख्या:** कुल 1,286 पिक्सेल (35.03 हेक्टर) सम्भावित सतह पानी क्षेत्र पत्ता लाग्यो।

---

## ३. सडक सञ्जाल विच्छेद र बस्ती सम्पर्क
- **विच्छेदित सडक खण्डहरू:** 3,748
- **पूर्व-घटना सञ्जाल घटकहरू:** 181
- **पछिल्लो सञ्जाल घटकहरू:** 252
- **मूल्याङ्कन गरिएका बस्तीहरू:** 589
- **सम्भावित रूपमा छुटेका बस्तीहरू:** 18
- **अस्पताल डेटा स्थिति:** Historical hospital data not available in pre-event snapshot; town/city hubs utilized for modeled access.

---

## ४. प्रमाणित दाबीहरू (Grounded Claims)
यस प्रतिवेदनका सबै संख्यात्मक दाबीहरू `evidence.json` मा प्रमाणित अभिलेखसँग सम्बन्धित छन्:
- बाढी पिक्सेल (`CLAIM-trishuli_benchmark_verified-FLOOD-PIXELS`): 1,286 pixels
- बाढी क्षेत्र (`CLAIM-trishuli_benchmark_verified-FLOOD-AREA`): 35.03 ha
- प्रभावित भवन (`CLAIM-trishuli_benchmark_verified-AFFECTED-BUILDINGS`): 195 buildings
- प्रभावित सडक (`CLAIM-trishuli_benchmark_verified-AFFECTED-ROADS`): 115 features (59.26 km)
- प्रभावित पुल (`CLAIM-trishuli_benchmark_verified-AFFECTED-BRIDGES`): 13 bridges
- विच्छेदित बस्ती (`CLAIM-trishuli_benchmark_verified-CUTOFF-SETTLEMENTS`): 18 settlements

---

## ५. सीमितताहरू
- The flood output is a modelled potential inundation candidate, not confirmed physical damage.
- Potentially affected assets are based on candidate spatial overlap; not confirmed structural destruction.
- Potentially cut-off settlements represent modelled topological network disconnections, not confirmed real-world isolation.
- Validation layers (EMSR927 / UNOSAT) are strictly checking-only and excluded from analytical pipelines.
- This system is an educational and research prototype for the Multimodal AI Hackathon 2026.
- Historical hospital data was unavailable in the pre-event snapshot; municipal town/city hubs were utilized for modeled road connectivity.

---

## ६. डेटा स्रोत र प्रतिलिपि अधिकार
- Copernicus Sentinel-1 / Sentinel-2 डेटा (ESA)।
- Copernicus WorldDEM-30 (DLR e.V. / Airbus)।
- पूर्व-बाढी OpenStreetMap डेटा (© OpenStreetMap contributors, ODbL 1.0)।
- EMSR927 / UNOSAT डेटा उत्पादन प्रणालीबाट पूर्ण रूपमा अलग राखिएको छ।
