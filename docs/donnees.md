# Données

Généré par `scripts/make_splits.py` : ne pas modifier à la main.

- Source : Tobi-Bueck/customer-support-tickets (Hugging Face), révision `ddf1c81a5475992c4fa6752bf1e8b4e31f07bbeb`.
- 28587 tickets lus, 15 doublons retirés (t01980, t05395, t08076, t11132, t11625, t13485, t14668, t15127, t16823, t23617, t25342, t25573, t26401, t27129, t27889), 28572 gardés.
- Découpage stratifié par (langue, file), graine 2026, fractions (0.7, 0.15, 0.15) : train 19998, validation 4287, test 4287.

### Files (catégorie à prédire)

| queue | train | validation | test | total | part |
|---|---|---|---|---|---|
| Technical Support | 5852 | 1254 | 1254 | 8360 | 29.3 % |
| Product Support | 3671 | 787 | 787 | 5245 | 18.4 % |
| Customer Service | 2985 | 640 | 640 | 4265 | 14.9 % |
| IT Support | 2402 | 515 | 515 | 3432 | 12.0 % |
| Billing and Payments | 1951 | 418 | 418 | 2787 | 9.8 % |
| Returns and Exchanges | 1005 | 216 | 216 | 1437 | 5.0 % |
| Service Outages and Maintenance | 802 | 173 | 173 | 1148 | 4.0 % |
| Sales and Pre-Sales | 642 | 138 | 138 | 918 | 3.2 % |
| Human Resources | 404 | 86 | 86 | 576 | 2.0 % |
| General Inquiry | 284 | 60 | 60 | 404 | 1.4 % |

### Priorités

| priority | train | validation | test | total | part |
|---|---|---|---|---|---|
| medium | 7975 | 1760 | 1774 | 11509 | 40.3 % |
| high | 7876 | 1651 | 1644 | 11171 | 39.1 % |
| low | 4147 | 876 | 869 | 5892 | 20.6 % |

### Langues

| language | train | validation | test | total | part |
|---|---|---|---|---|---|
| en | 11431 | 2448 | 2448 | 16327 | 57.1 % |
| de | 8567 | 1839 | 1839 | 12245 | 42.9 % |

### Types

| type | train | validation | test | total | part |
|---|---|---|---|---|---|
| Incident | 8056 | 1698 | 1707 | 11461 | 40.1 % |
| Request | 5697 | 1209 | 1277 | 8183 | 28.6 % |
| Problem | 4205 | 944 | 860 | 6009 | 21.0 % |
| Change | 2040 | 436 | 443 | 2919 | 10.2 % |
