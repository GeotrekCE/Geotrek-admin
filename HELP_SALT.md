= 1
```bash
cd ~/workspace/geotrek
git pull github
git pull deploy
git checkout -b mydeploycg44 deploy/master
git merge github/master
git push deploy HEAD:master
git push prod-geotre042 HEAD:master
```

= 2
```bash
ssh prod-geotre042.makina-corpus.net
cd  /srv/projects/geotrek/project
git fetch --all
git reset --hard gitlab/master
salt-call --local -lall mc_project.deploy geotrek only=install,fixperms
```

