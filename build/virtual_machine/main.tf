
resource "google_service_account" "service_account" {
  account_id   = "service-account-vm-3"
  display_name = "Service Account VM 3"
  project      = var.project_id
}


resource "google_project_iam_member" "service-account-iam" {
  provider = google-beta
  project = var.project_id
  role               = "roles/iam.serviceAccountUser"
  member          =  "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_project_iam_member" "storage-object-iam" {
  provider = google-beta
  project = var.project_id
  role               = "roles/storage.objectCreator"
  member          =  "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_project_iam_member" "artifact-registry-iam" {
  provider = google-beta
  project = var.project_id
  role               = "roles/artifactregistry.reader"
  member          =  "serviceAccount:${google_service_account.service_account.email}"
}


resource "google_compute_instance" "instance-web-scrap" {
  boot_disk {
    auto_delete = true
    device_name = "instance-web-scrap"

    initialize_params {
      image = "projects/debian-cloud/global/images/debian-12-bookworm-v20240213"
      size  = 10
      type  = "pd-balanced"
    }

    mode = "READ_WRITE"
  }

  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false

  labels = {
    goog-ec-src = "vm_add-tf"
  }

  machine_type = "e2-medium"

  metadata = {
    startup-script = "#! /bin/bash\nsudo apt-get update\nsudo apt-get install ca-certificates curl\nsudo install -m 0755 -d /etc/apt/keyrings\nsudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc\nsudo chmod a+r /etc/apt/keyrings/docker.asc\necho \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null\nsudo apt-get update\nsudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin\nsudo groupadd docker\nsudo usermod -aG docker $${USER}\nsudo chmod 666 /var/run/docker.sock\nsudo systemctl restart docker"
  }

  name = "instance-web-scrap"

  network_interface {
    access_config {
      network_tier = "PREMIUM"
    }

    queue_count = 0
    stack_type  = "IPV4_ONLY"
    subnetwork  = "projects/enduring-branch-413218/regions/us-central1/subnetworks/default"
  }

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
    provisioning_model  = "STANDARD"
  }

  service_account {
    email  = google_service_account.service_account.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }

  zone = "us-central1-c"
}
