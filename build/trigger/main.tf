data "local_file" "github_token_file" {
  filename = var.github_token_file
}

resource "google_secret_manager_secret" "github_token_secret" {
    project =  var.project_id
    secret_id = "secret_git_hub"

  replication {
    auto {}
  }
}

data "google_iam_policy" "serviceagent_secretAccessor" {
    binding {
        role = "roles/secretmanager.secretAccessor"
        members = ["serviceAccount:service-418428393130@gcp-sa-cloudbuild.iam.gserviceaccount.com"]
    }
}

resource "google_secret_manager_secret_iam_policy" "policy" {
  project = google_secret_manager_secret.github_token_secret.project
  secret_id = google_secret_manager_secret.github_token_secret.secret_id
  policy_data = data.google_iam_policy.serviceagent_secretAccessor.policy_data
}

resource "google_secret_manager_secret_version" "github_token_secret_version" {
    secret = google_secret_manager_secret.github_token_secret.id
    secret_data = jsondecode(data.local_file.github_token_file.content)["github_token"]
}


resource "google_cloudbuildv2_connection" "my-connection" {
  project = var.project_id 
  location = var.region
  name = "connection_cloud_build"

  github_config {
    app_installation_id = var.app_installation_id
    authorizer_credential {
      oauth_token_secret_version = google_secret_manager_secret_version.github_token_secret_version.id
    }
  }
}

resource "google_cloudbuildv2_repository" "my-repository" {
  name = var.repositorio
  parent_connection = google_cloudbuildv2_connection.my-connection.id
  remote_uri = var.remote_uri
}

resource "google_cloudbuild_trigger" "repo-trigger" {
  location = var.region
  name= "cloud-build-terraform"

  repository_event_config {
    repository = google_cloudbuildv2_repository.my-repository.id
    push {
      branch = "^main$"
    }
  }

  filename = "cloudbuild.yaml"
}