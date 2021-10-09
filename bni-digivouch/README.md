# CR28828

# How To Build

1. Build image docker dengan command:
```bash
docker-compose build --build-arg HTTPS_PROXY=http://192.168.45.105:8080
```
2. Push image docker yang terbentuk dengan command:
```bash
docker-compose push
```
3. Deploy image yang sudah di-push dengan command:
```bash
docker-compose config | docker stack deploy -c - digivouch
```

Note: jika update source, pastikan untuk remove dahulu stack dan image dengan 

```
docker stack rm <nama stack>
```

untuk tau nama stack

```
docker stack ls 
```
cari digivouch

hapus image
```
docker image rm jtl-tkgiharbor.hq.bni.co.id/soadev/database-write:0.1 jtl-tkgiharbor.hq.bni.co.id/soadev/ayopop-proxy:0.1 jtl-tkgiharbor.hq.bni.co.id/soadev/digivouch-graphql:0.1 jtl-tkgiharbor.hq.bni.co.id/soadev/core-payment:0.1 jtl-tkgiharbor.hq.bni.co.id/soadev/ayopop-callback-getter:0.1 jtl-tkgiharbor.hq.bni.co.id/soadev/database-write:0.1
```
