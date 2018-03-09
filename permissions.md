Permissions
===========

Permissions of the Django Admin Site are managed through Django. Documentation can be find online for this part, e.g. [Permissions in Django Admin](http://kracekumar.com/post/141377389440/permissions-in-django-admin), [The Django Book](https://djangobook.com/users-groups-permissions/).

On the other hand, the API provided by this server comes with an object-based permissions model that is documented here.

The main idea behind this model is that there's a fixed set of [rules](api/rules.py) that are applied, regulated by groups. Rules are roughly based on matrix of the form (read, write)⋅(user, group, others).

Maps:
  - can be viewed if
    - user is the author of the map
    - user is in the same group as the map
    - map is in the PUBLIC_GROUP
  - can be changed if
    - user is the author of the map
  - can be deleted if
    - user is the author of the map

Layers:
  - can be viewed if
    - user is the author of a map containing this layer
    - user is in the same group as a map containing this layer
    - a map containing this layer is in the PUBLIC_GROUP

Metadata, Alias:
  - can always be viewed
  - can be changed if
    - user is in the DEFAULT_GROUP


Groups intersections are computed based on groups that are attached to users with ```django.contrib.auth``` module and groups attached to maps in ```sdi.api.permissiongroup```. Both accessible in the Django Admin Site.

## Settings

```DEFAULT_GROUP``` is the default group name that will be set on a map which is not otherwise attached to a group through a ```PermissionGroup```. This group name should be the same as your main userbase group. This setting is required.

```PUBLIC_GROUP``` denotes which group will make maps visible to anonymous users (i.e. visitors). This setting is required.

Note that if those group do not exist yet, they'll be created.

