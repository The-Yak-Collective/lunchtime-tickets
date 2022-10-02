#!/usr/bin/env python3

# Import necessary packages.
#
import os

# Update secret function.
#
def update(repo_handle, var_name, base = "", add = "ADD", remove = "REMOVE", separator = "_"):

	# Pull secrets (base/add/remove) from the environment. We assume
	# that secret lists are whitespace-separated. Note that we store the
	# intermediate string value here as well so that we can use it later
	# to determine if we really need to update the secret in GitHub
	# (this avoids unnecessary noise in the audit logs).
	#
	secret_name = separator.join(filter(None, [var_name, base]))
	secrets_string = os.environ[secret_name].strip()
	secrets = secrets_string.split()

	secrets_to_add_name = separator.join([var_name, add])
	secrets_to_add_string = os.environ[secrets_to_add_name].strip()
	secrets_to_add = secrets_to_add_string.split()

	secrets_to_remove_name = separator.join([var_name, remove])
	secrets_to_remove_string = os.environ[secrets_to_remove_name].strip()
	secrets_to_remove = secrets_to_remove_string.split()

	# Take the union of secrets and secrets_to_add and then remove
	# secrets_to_remove.
	#
	new_secrets = list((set(secrets).union(set(secrets_to_add))).difference(set(secrets_to_remove))).sort()

	# Update the base secret value with the value derived in
	# new_secrets, but only if there's been a change.
	#
	if len(new_secrets) == 0:
		new_secrets_string = " "
	else:
		new_secrets_string = "\n".join(new_secrets)
	
	if new_secrets_string.strip() != secrets_string:
		repo_handle.create_secret(secret_name, new_secrets_string)

	# Blank out secret add/remove values, if necessary.
	#
	if len(secrets_to_add) != 0:
		repo_handle.create_secret(secrets_to_add_name, " ")
	if len(secrets_to_remove) != 0:
		repo_handle.create_secret(secrets_to_remove_name, " ")

	# Return the list of secret values (with add/removes).
	#
	return(new_secrets)
