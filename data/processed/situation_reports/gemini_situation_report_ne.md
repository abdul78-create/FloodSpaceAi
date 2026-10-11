# बाढी अवस्था प्रतिवेदन

## अवस्थाको संक्षिप्त विवरण

यो विश्लेषण {'event': 'August 2026 Trishuli flood', 'analysis_area': 'Trishuli valley AOI', 'osm_snapshot': '2026-07-27T00:00:00Z'} केस स्टडीका लागि FloodSpaceAI को
उपग्रह तथा पूर्व-घटना OpenStreetMap तथ्यांकमा आधारित छ।

## बाढीको सम्भावित प्रभाव क्षेत्र

प्रणालीले Sentinel-1 SAR परिवर्तन, Sentinel-2 NDWI परिवर्तन,
घटना-पछिको पानीको अवस्था, घटना-अघिको गैर-पानी अवस्था र
connected-component filtering प्रयोग गरेर सम्भावित inundation
candidate तयार गरेको छ।

प्रणालीमा 1286 flood pixels र
84 flood polygons पहिचान भएका छन्।

यी परिणामहरू **सम्भावित inundation** हुन् र निश्चित वास्तविक
बाढी क्षेत्रको पुष्टि मानिनु हुँदैन।

## सम्भावित रूपमा प्रभावित पूर्वाधार

प्रणालीले निम्न पूर्वाधारहरूलाई सम्भावित रूपमा प्रभावित भनेर
पहिचान गरेको छ:

- भवन: 195
- सडक: 115
- पुल: 13

यी संख्या पुष्टि भएको भौतिक क्षति वा विनाशको संख्या होइनन्।

## सम्भावित रूपमा सम्पर्क विच्छेद भएका बस्तीहरू

कुल 600 बस्तीमध्ये
589 बस्तीको road-network connectivity
विश्लेषण गरिएको छ।

विश्लेषणमा 3 town/city hubs प्रयोग गरिएको छ।

18 बस्तीहरू सम्भावित रूपमा cut off देखिएका छन्।

यो road-network model मा देखिएको disconnect हो र वास्तविक
मैदानस्तरीय isolation को पुष्टि होइन।

## विधि

विश्लेषणमा Sentinel-1 pre/post SAR तुलना,
Sentinel-2 optical comparison, NDWI परिवर्तन,
पूर्व-घटना OpenStreetMap infrastructure र
road-network connectivity प्रयोग गरिएको छ।

## सीमितताहरू

- सम्भावित inundation output पुष्टि भएको flood extent होइन।
- Sentinel-2 optical imagery मा cloud contamination रहेको छ।
- सम्भावित रूपमा प्रभावित infrastructure पुष्टि भएको damage होइन।
- सम्भावित cut-off settlements वास्तविक isolation को पुष्टि होइन।
- उपलब्ध historical data सीमितताका कारण hospital connectivity
  पूर्ण रूपमा समावेश गरिएको छैन।

## तथ्यांक तथा स्रोत

OpenStreetMap पूर्व-घटना snapshot:

2026-07-27T00:00:00Z

यो प्रतिवेदन प्रणालीको evidence dataset बाट मात्र
संख्यात्मक जानकारी प्रयोग गरेर तयार गरिएको हो।
