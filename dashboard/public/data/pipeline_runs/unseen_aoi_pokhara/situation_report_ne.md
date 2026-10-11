# FloodSpaceAI स्थिति प्रतिवेदन — Run `unseen_aoi_pokhara`

**घटना मिति:** `2026-09-15`  
**विश्लेषण क्षेत्र (AOI):** `[83.95, 28.18, 84.05, 28.28]`  
**डेटा मोड:** `UNKNOWN`  
**उत्पादन समय:** `2026-10-09T09:43:09.611851+00:00`

---

## १. अवस्थाको संक्षिप्त विवरण
FloodSpaceAI ले Copernicus Sentinel उपग्रह डेटा र पूर्व-बाढी OpenStreetMap पूर्वाधारको प्रयोग गरेर बाढी अवस्थाको विश्लेषण गरेको छ।

- सम्भावित बाढी पिक्सेल: **0**
- सम्भावित बाढी क्षेत्र: **0.00 ha**
- सम्भावित प्रभावित भवन: **0**
- सम्भावित प्रभावित सडक: **0** (0.00 km)
- सम्भावित प्रभावित पुल: **0**
- सम्भावित रूपमा सडक सम्पर्कबाट छुटेका बस्ती: **0**

> **वैज्ञानिक सूचना:** यी तथ्याङ्कहरू मोडेल गरिएका सम्भावित बाढी क्षेत्र र सडक सञ्जाल विच्छेदमा आधारित हुन्। वास्तविक भौतिक क्षति वा पूर्ण अलगावको पुष्टि गरिएको होइन।

---

## २. सीमितताहरू
- The flood output is a modelled potential inundation candidate, not confirmed physical damage.
- Potentially affected assets are based on candidate spatial overlap; not confirmed structural destruction.
- Potentially cut-off settlements represent modelled topological network disconnections, not confirmed real-world isolation.
- Validation layers (EMSR927 / UNOSAT) are strictly checking-only and excluded from analytical pipelines.
- This system is an educational and research prototype for the Multimodal AI Hackathon 2026.

---

## ३. डेटा स्रोत र प्रतिलिपि अधिकार
- Copernicus Sentinel-1 / Sentinel-2 डेटा।
- Copernicus WorldDEM-30।
- पूर्व-बाढी OpenStreetMap डेटा (© OpenStreetMap contributors)।
- EMSR927 / UNOSAT डेटा उत्पादन प्रणालीबाट पूर्ण रूपमा अलग राखिएको छ।
