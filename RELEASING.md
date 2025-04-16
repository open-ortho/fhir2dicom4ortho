# Release checklist: How to release a new version.

1. `invoke build` and run the docker image and test against it. Is it working?
2. Check version number and decide what version to release into.
3. Create `release`:  e.g. `git flow release start 0.X.0`
4. Bump the version with major, minor or patch and then `bumpversion release` as required.
5. `git merge main`: merge main into here, and fix merge errors.
6. Update release notes in `CHANGELOG.md` with major changes of this release. You might want to compare this release branch against master to see logs.
7. Check that README.md is still current.
8. `invoke deploy`: this will run tests, build image and deploy it.
9. If all goes well, then merge branch into master: `git flow release finish`. The GitHub Actions will take care of deploying to PyPi.
10. `git push --tags`
11. Once back in develop branch, `bumpversion patch` to bump up a patch and add `-dev` suffix.