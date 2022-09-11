#!/usr/bin/env python3

# Import necessary packages
#
import os

# Update secret function
#
def update(repo_handle, var_name, base = "", add = "ADD", remove = "REMOVE", separator = "_"):

	# Pull secrets (base/add/remove) from the environment. We assume
	# that secret lists are whitespace-separated.
	#
	secret_name = separator.join([var_name, base])
	secrets = os.environ[secret_name].split()

	secrets_to_add_name = separator.join([var_name, add])
	secrets_to_add = os.environ[secrets_to_add_name].split()

	secrets_to_remove_name = separator.join([var_name, remove])
	secrets_to_remove = os.environ[secrets_to_remove_name].split()

	# Take the union of secrets and secrets_to_add and then remove
	# secrets_to_remove.
	#
	new_secrets = list((set(secrets).union(set(secrets_to_add))).difference(set(secrets_to_remove)))

	# Update the base secret value with the value derived in new_secrets
	#
	repo_handle.create_secret(secret_name, "\n".join(new_secrets))

	# Blank out secret add/remove values
	#
	repo_handle.create_secret(secrets_to_add_name, "")
	repo_handle.create_secret(secrets_to_remove_name, "")

	# Return the list of secret values (with add/removes)
	#
	return(new_secrets)
