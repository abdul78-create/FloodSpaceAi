# FloodSpaceAI स्थिति प्रतिवेदन — Run `narayani_2024_live`

**घटना मिति:** `2024-08-20`  
**विश्लेषण क्षेत्र (AOI):** `[84.3, 27.55, 84.5, 27.72]`  
**OpenStreetMap स्न्यापसट मिति:** `2024-08-13T00:00:00Z`  
**डेटा मोड:** `LIVE_AUTHORITATIVE_SATELLITE_RETRIEVAL`  
**उत्पादन समय:** `2026-10-09T15:34:31.930558+00:00`

---

## १. अवस्थाको संक्षिप्त विवरण
FloodSpaceAI ले Copernicus Sentinel उपग्रह डेटा र पूर्व-बाढी OpenStreetMap पूर्वाधारको प्रयोग गरेर बाढी अवस्थाको विश्लेषण गरेको छ।

- सम्भावित बाढी पिक्सेल: **0**
- सम्भावित बाढी क्षेत्र: **0.00 ha**
- सम्भावित प्रभावित भवन: **0** (एक्सपोजर ओभरले)
- सम्भावित प्रभावित सडक: **0** (0.00 km)
- सम्भावित प्रभावित पुल: **0**
- सम्भावित रूपमा सडक सम्पर्कबाट छुटेका बस्ती: **0**

> **वैज्ञानिक सूचना:** यी तथ्याङ्कहरू मोडेल गरिएका सम्भावित बाढी क्षेत्र र सडक सञ्जाल विच्छेदमा आधारित हुन्। वास्तविक भौतिक क्षति वा पूर्ण अलगावको पुष्टि गरिएको होइन।

---

## २. उपग्रह अवलोकन र कभरेज
- **SAR सेन्सर:** Sentinel-1 C-band synthetic aperture radar (सबै मौसममा अवलोकन गर्न सकिने)।
- **अप्टिकल सेन्सर:** Sentinel-2 multispectral MSI (Scene Classification Layer बादल मास्किङ गरिएको)।
- **अप्टिकल कभरेज अवस्था:** Generated 0 candidate pixels across 0 clusters.।
- **व्याख्या:** हालको SAR र अप्टिकल थ्रेसहोल्ड अनुसार कुनै सम्भावित बाढी पिक्सेल फेला परेन। यसले बाढी नआएको प्रमाणित गर्दैन, तर विश्लेषणात्मक मापदण्ड पूरा नगरेको जनाउँछ।

---

## ३. सडक सञ्जाल विच्छेद र बस्ती सम्पर्क
- **विच्छेदित सडक खण्डहरू:** 0
- **पूर्व-घटना सञ्जाल घटकहरू:** 35
- **पछिल्लो सञ्जाल घटकहरू:** 35
- **मूल्याङ्कन गरिएका बस्तीहरू:** 25
- **सम्भावित रूपमा छुटेका बस्तीहरू:** 0
- **अस्पताल डेटा स्थिति:** Historical hospital locations present and evaluated.

---

## ४. प्रमाणित दाबीहरू (Grounded Claims)
यस प्रतिवेदनका सबै संख्यात्मक दाबीहरू `evidence.json` मा प्रमाणित अभिलेखसँग सम्बन्धित छन्:
- बाढी पिक्सेल (`CLAIM-narayani_2024_live-FLOOD-PIXELS`): 0 pixels
- बाढी क्षेत्र (`CLAIM-narayani_2024_live-FLOOD-AREA`): 0.00 ha
- प्रभावित भवन (`CLAIM-narayani_2024_live-AFFECTED-BUILDINGS`): 0 buildings
- प्रभावित सडक (`CLAIM-narayani_2024_live-AFFECTED-ROADS`): 0 features (0.00 km)
- प्रभावित पुल (`CLAIM-narayani_2024_live-AFFECTED-BRIDGES`): 0 bridges
- विच्छेदित बस्ती (`CLAIM-narayani_2024_live-CUTOFF-SETTLEMENTS`): 0 settlements

---

## ५. सीमितताहरू
- The flood output is a modelled potential inundation candidate, not confirmed physical damage.
- Potentially affected assets are based on candidate spatial overlap; not confirmed structural destruction.
- Potentially cut-off settlements represent modelled topological network disconnections, not confirmed real-world isolation.
- Validation layers (EMSR927 / UNOSAT) are strictly checking-only and excluded from analytical pipelines.
- This system is an educational and research prototype for the Multimodal AI Hackathon 2026.

---

## ६. डेटा स्रोत र प्रतिलिपि अधिकार
- Copernicus Sentinel-1 / Sentinel-2 डेटा (ESA)।
- Copernicus WorldDEM-30 (DLR e.V. / Airbus)।
- पूर्व-बाढी OpenStreetMap डेटा (© OpenStreetMap contributors, ODbL 1.0)।
- EMSR927 / UNOSAT डेटा उत्पादन प्रणालीबाट पूर्ण रूपमा अलग राखिएको छ।
