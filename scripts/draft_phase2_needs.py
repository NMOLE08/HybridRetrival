"""Author question-first needs without reading source passages or retrieval outputs."""
import json
import random
from pathlib import Path

# These information needs were written from general security knowledge before
# acquiring new record content. Questions can contain errors and require review.
CVE_NEEDS = [
('CVE-2021-41773','What Apache HTTP Server path traversal is associated with CVE-2021-41773?'),
('CVE-2021-42013','How does CVE-2021-42013 affect Apache HTTP Server traversal defenses?'),
('CVE-2021-3156','What sudo heap overflow is described under CVE-2021-3156?'),
('CVE-2022-0847','How can the Linux pipe vulnerability CVE-2022-0847 affect files?'),
('CVE-2016-5195','What Linux memory handling race is identified as CVE-2016-5195?'),
('CVE-2024-3400','What network-device vulnerability is tracked by CVE-2024-3400?'),
('CVE-2023-22515','Which Confluence authorization problem is described by CVE-2023-22515?'),
('CVE-2023-4966','What Citrix information disclosure is associated with CVE-2023-4966?'),
('CVE-2023-3519','What type of security issue affects Citrix under CVE-2023-3519?'),
('CVE-2021-26084','What Confluence component is affected by CVE-2021-26084?'),
('CVE-2022-26134','How does CVE-2022-26134 affect Confluence deployments?'),
('CVE-2022-1388','What management interface issue is recorded as CVE-2022-1388?'),
('CVE-2023-20198','What Cisco management-interface flaw is identified by CVE-2023-20198?'),
('CVE-2020-5902','What affected network management functionality is described in CVE-2020-5902?'),
('CVE-2022-40684','What authentication bypass is tracked by CVE-2022-40684?'),
('CVE-2023-27997','What is the Fortinet issue recorded under CVE-2023-27997?'),
('CVE-2024-21887','What command injection vulnerability corresponds to CVE-2024-21887?'),
('CVE-2024-1709','What authentication weakness is associated with CVE-2024-1709?'),
('CVE-2022-47966','Which application components are affected by CVE-2022-47966?'),
('CVE-2021-21972','What VMware vCenter flaw is described by CVE-2021-21972?'),
('CVE-2021-22005','What upload-related security problem is tracked as CVE-2021-22005?'),
('CVE-2023-20887','What VMware network management problem is associated with CVE-2023-20887?'),
('CVE-2023-27350','How is PaperCut affected by the vulnerability CVE-2023-27350?'),
('CVE-2023-36884','What security weakness is assigned CVE-2023-36884?'),
('CVE-2023-38831','What archive handling issue is associated with CVE-2023-38831?'),
('CVE-2021-40444','What Windows document-rendering issue is tracked by CVE-2021-40444?'),
('CVE-2023-50164','Which Struts upload weakness is identified as CVE-2023-50164?'),
('CVE-2022-42889','What Apache text-processing issue corresponds to CVE-2022-42889?'),
('CVE-2018-7600','What Drupal vulnerability is assigned CVE-2018-7600?'),
('CVE-2019-11510','What VPN file-access problem is described in CVE-2019-11510?'),
('CVE-2020-0688','Which Exchange control is affected by CVE-2020-0688?'),
('CVE-2020-0796','What SMB protocol weakness is tracked by CVE-2020-0796?'),
('CVE-2021-34473','What Exchange server issue is described by CVE-2021-34473?'),
('CVE-2019-18935','What Telerik upload component vulnerability is CVE-2019-18935?'),
('CVE-2020-2555','What Oracle product vulnerability is associated with CVE-2020-2555?'),
('CVE-2023-46747','What product and weakness are associated with CVE-2023-46747?'),
('CVE-2023-34362','EXCLUDE: this identifier appeared in Phase 1 test.'),
]

FEATURES=[('CPU_CORES_NUM','How many processor cores are specified for {chip}?'),
          ('GPIO_PIN_COUNT','How many GPIO pins are defined for {chip}?'),
          ('UART_NUM','What UART controller count is specified for {chip}?'),
          ('SPI_PERIPH_NUM','What SPI peripheral count does {chip} declare?'),
          ('WIFI_SUPPORTED','Do the capability definitions indicate Wi-Fi support for {chip}?'),
          ('BLE_SUPPORTED','Do the definitions indicate Bluetooth Low Energy support for {chip}?')]
TEST_FEATURES=[('ADC_SUPPORTED','Does {chip} provide analog-to-digital conversion capability?'),
 ('DAC_SUPPORTED','Does {chip} provide a digital-to-analog converter?'),
 ('I2C_SUPPORTED','What inter-integrated circuit support is defined for {chip}?'),
 ('I2S_SUPPORTED','What inter-IC sound capability is defined for {chip}?'),
 ('RMT_SUPPORTED','Is a remote-control peripheral supported by {chip}?'),
 ('GPTIMER_SUPPORTED','Do the capability definitions show general-purpose timers for {chip}?'),
 ('USB_OTG_SUPPORTED','Is USB on-the-go supported by {chip}?'),
 ('TWAI_SUPPORTED','Does {chip} declare two-wire automotive interface capability?'),
 ('PCNT_SUPPORTED','Is pulse counting supported by {chip}?'),
 ('LEDC_SUPPORTED','Do the definitions for {chip} include LED control capability?')]
NATURAL=[
('SOC_CPU_CORES_NUM','Find a hardware capability definition giving a processor core count.'),
('SOC_GPIO_PIN_COUNT','Locate a chip capability definition specifying the number of general-purpose I/O pins.'),
('SOC_UART_NUM','Which capability declaration gives the number of universal asynchronous receiver transmitters?'),
('SOC_SPI_PERIPH_NUM','Find hardware definitions that specify how many serial peripheral interface controllers exist.'),
('SOC_WIFI_SUPPORTED','Locate a capability definition indicating whether wireless LAN is supported.'),
('SOC_BLE_SUPPORTED','Find a capability declaration covering Bluetooth Low Energy support.'),
('SOC_ADC_SUPPORTED','Which chip capability file declares analog-to-digital conversion support?'),
('SOC_DAC_SUPPORTED','Locate a definition covering digital-to-analog converter availability.'),
('SOC_I2C_SUPPORTED','Find a capability definition about inter-integrated circuit support.'),
('SOC_I2S_SUPPORTED','Which hardware capability definitions mention inter-IC sound support?'),
('SOC_RMT_SUPPORTED','Find a chip definition describing remote-control peripheral support.'),
('SOC_GPTIMER_SUPPORTED','Locate a capability declaration about general-purpose hardware timers.'),
('SOC_USB_OTG_SUPPORTED','Find a chip capability definition about USB on-the-go support.'),
('SOC_TWAI_SUPPORTED','Locate a definition of two-wire automotive interface capability.'),
('SOC_PCNT_SUPPORTED','Find a hardware capability declaration covering pulse counting.'),
('SOC_LEDC_SUPPORTED','Which capability file covers LED control peripheral support?'),
('SOC_MCPWM_SUPPORTED','Locate a definition about motor-control pulse-width modulation support.'),
('SOC_SDM_SUPPORTED','Find a chip capability declaration concerning sigma-delta modulation support.')]


def main():
    path=Path('data/phase2/needs_draft.jsonl')
    if path.exists(): raise FileExistsError('Preserve existing draft needs; do not overwrite')
    old={json.loads(line)['text'] for line in Path('data/technical/queries_test.jsonl').read_text(encoding='utf-8').splitlines()}
    old_ids={json.loads(line)['doc_id'].upper() for line in Path('data/technical/corpus.jsonl').read_text(encoding='utf-8').splitlines()}
    cves=[(i,q) for i,q in CVE_NEEDS if i not in old_ids and not q.startswith('EXCLUDE:')]
    random.Random(42).shuffle(cves)
    rows=[]
    for n,(target,text) in enumerate(cves):
        rows.append({'need_id':f'cve-{n+1:02d}','split':'dev' if n<12 else 'test','topic_id':target,'query':text,'query_type':'identifier','family':'cve','target':target})
    chips=[('ESP32-C2','dev'),('ESP32-C5','dev'),('ESP32-S2','dev'),('ESP32-H2','dev'),('ESP32-C2','dev'),('ESP32-C5','dev'),('ESP32-C3','test'),('ESP32-C6','test'),('ESP32-S3','test'),('ESP32-P4','test'),('ESP32-C61','test'),('ESP32','test'),('ESP32-C3','test'),('ESP32-C6','test'),('ESP32-S3','test'),('ESP32-P4','test')]
    for n,(chip,split) in enumerate(chips):
        feature,template=FEATURES[n] if split=='dev' else TEST_FEATURES[n-6]
        rows.append({'need_id':f'esp-{n+1:02d}','split':split,'topic_id':chip,'query':template.format(chip=chip),'query_type':'identifier','family':'esp32','target':chip,'expected_macro':'SOC_'+feature})
    for n,(macro,text) in enumerate(NATURAL):
        rows.append({'need_id':f'natural-{n+1:02d}','split':'dev' if n<6 else 'test','topic_id':macro,'query':text,'query_type':'natural','family':'none','target':None,'expected_macro':macro})
    for row in rows:
        row['origin']='agent_authored_question_first';row['review_status']='unreviewed_draft';row['evidence_status']='not_yet_checked'
        if row['query'] in old: raise ValueError('Old test query reused')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8',newline='\n')
    print(f'Wrote {len(rows)} unreviewed question-first drafts without reading Phase 2 passages or rankings: {path}')


if __name__=='__main__':main()
