# GCP notes
### A compilation of useful snippets and commands to be used on Google Cloud Platform Services. 

A repo to collect small tricks and tips I usually apply for both personal and professional projects. Feel free to comment or add any suggestion by PR.

### Few notes about GCP
#### 1. GCP structure 
GCP is organised as a big directory of "folders". When we talk about BigQuery, the organisation is very similar to other RDBMS (Datasets and tables/views). However, when it comes to the rest of applications in GCP, the main structure is the Project. A project is the main _space_ where you will be working or storing information.
#### 2. IAM roles
AS Google explain in its documentation: _"With IAM, you manage access control by defining who (identity) has what access (role) for which resource. For example, Compute Engine virtual machine instances, Google Kubernetes Engine (GKE) clusters, and Cloud Storage buckets are all Google Cloud resources. The organizations, folders, and projects that you use to organize your resources are also resources. In IAM, permission to access a resource isn't granted directly to the end user. Instead, permissions are grouped into roles, and roles are granted to authenticated members. An IAM policy defines and enforces what roles are granted to which members, and this policy is attached to a resource. When an authenticated member attempts to access a resource, IAM checks the resource's policy to determine whether the action is permitted."_
