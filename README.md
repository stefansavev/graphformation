# Infrastructure Provisioning Tools and Resource Graphs

*Do DevOps Think in Terms of Graphs?*

Probably not! But the designers of modern DevOps tools obviously do.
Consider AWS CloudFormation, Azure Resource Manager, Google Cloud Deployment Manager or Terraform.
Those tools are used to create or *provision* a complete software solution on AWS, Azure or Google Cloud respectively. They are a *"must know"* for any organization using the cloud.

They may seems complex at first, but underlying the tools is a simple conceptual model of thinking of computing resources as a graph. This is a useful mental model which can help developers
and DevOps engineers quickly get comfortable with those tools.

A *resource* is a virtual representation of a physical computing object such as a virtual machine, an API, a folder, or a database table. 
Resources have properties. For example a virtual machine can have a name, an operating system and so on. **Properties can be primitives like strings or numbers**, or **references to other resources**.


## Example Architecture

Below is a sample architecture in AWS. 

 ![Your infrastructure as a graph](https://github.com/stefansavev/graphformation/blob/master/images/infrastructure-graph.png)

In the example above, CloudFront references APIGateway, which references two lambda functions, each of which references a DynamoDB database table or an S3 bucket. Arrows are from the referencing object to the referenced ones.

Operationally, you can use an algorithm to create the corresponding infrastructure from this graph. Here is one algorithm:

- first create the DynamoDB table and s3 bucket (in parallel) as nothing points to them, 
- then create the lambda functions (again in parallel) and so on. 

The DynamoDB table and s3 bucket **can be created in parallel** as they are independent.

Of course, one can also use other approaches. For example,
- create the CloudFront object (the one in the bottom)
- create the rest
- update the reference in CloudFront.

This makes sense from a practical perspective because CloudFront takes longest to create. Updating it is simpler.
This is possible, if we know which properties of a resource are *mutable* and which are *immutable*. CloudFormation makes this clear in its specification.


# GraphFormation: a Tiny Toy CloudFormation
 
To make things more clearer let's say we design of own "GraphFormation" tool or language. As an example, we want to create (*provision*) a directory with two files, one of which is downloaded from a web server. Here is how I could write a *provisioning* specification:

**Code Snippet 1**
```
mydir=directory(
  id="dir",
  location="/tmp/mydirectory"
)

file(
   id="contentfile",
   filename="file1",
   parent=ref(mydir),
   text="Lorem ipsum dolor"
)

file(
   id="downloadedfile",
   filename="file2",
   parent=ref(mydir),
   source="https://webserver.com/file.txt"
)
```

One can convert this representation to a graph, such as this one:

 ![Your infrastructure as a graph](https://github.com/stefansavev/graphformation/blob/master/images/sample-graphformation.png)


# Fighting Graphs with Abstraction

A graph is a monolithic object, and in software development *monolithic* is a bad word. In software development people like *abstractions*. Choosing the wrong level of abstraction can make or break a project.

Abstraction is so fundamental that it is introduced in the very first lecture of [Structure and Interpretation of Computer Programs, 1986](https://www.youtube.com/watch?v=2Op3QLzMgSY&list=PLE18841CABEA24090). For the purpose of this blog post, here is a nice picture to keep in our heads:

 ![The means of abstraction](https://github.com/stefansavev/graphformation/blob/master/images/means-of-abstraction.png)

Basically, what Abelson tells you is how to build a complex system. Setting up a cloud infrastructure with thousands of resources is *complex*. 
One implication is that you build bigger things out of smaller things. You build a program out of multiple files, which themselves consist of variables, functions, classes - all mechanisms to introduce structure in the designed solution. I know it sounds trivial but CloudFormation is a single file. 

For me CloudFormation is akin to Assembly Language because I find it too low level and lacking the typical abstractions available in a programming language like Python. I acknowledge that CloudFormation has some abstractions like variables, but it lacks support for first-class functions, multiple files and libraries.

In the next blog posts I will discuss some important features of CloudFormation that help with abstraction.
Those are Built-in functions, Macros, Custom Resources and Nested Templates.

My preferred way of using CloudFormation is via a *high-level programming language* such as Python. I like to *generate my CloudFormation template* with a library such as [troposphere](https://github.com/cloudtools/troposphere).

In contrast to CloudFormation, Terraform supports multiple files, and modules which allow code reuse. Modules are similar to functions in other programming languages.

## Metalinguistic Abstraction

In the very first lecture of  [Structure and Interpretation of Computer Programs, 1986](https://www.youtube.com/watch?v=2Op3QLzMgSY&list=PLE18841CABEA24090), Abelson gives one solution to tackling complexity: *metalinguistic abstraction*.

> In computer science, metalinguistic abstraction is the process of solving complex problems by creating a new language or vocabulary to better understand the problem space. It is a recurring theme in the seminal MIT textbook, the Structure and Interpretation of Computer Programs,...
> - Source: Wikipedia


![The means of abstraction](https://github.com/stefansavev/graphformation/blob/master/images/metalinguistic-abstraction.png)

 What this means in practical terms is, in any domain, but in particular in the domain of *infrastructure as code* we need to:

- find the vocabulary via which to talk about our domain
- connect primitives (aka the nouns in vocabulary) via a domain specific language 

## Vocabulary

The core *NOUN* we are looking for is *RESOURCE*. This is the *PRIMITIVE* that Abelson talks about.
It looks trivial, but neither 
[CloudFormation Concepts](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-whatis-concepts.html), nor [Terraform](https://www.terraform.io/intro/index.html) give this concept center stage.

I have more luck with [Google Cloud](https://cloud.google.com/deployment-manager/docs/fundamentals). For Computer Science Fundamentals, Google Cloud nails it.

From the very sentence, you know that these guys are hitting the nail on the head:

> A configuration describes all the resources you want for a single deployment."
> - Source: Google Cloud

Then they continue, just like you'd define your language semantics:

```
Each resource must contain three components:

name - ...
type - ...
properties - ...
```

It looks like Google's approach to design follows sound algorithmic & programming language design principles. 

## Domain-specific Languages

People started thinking about domain specific languages at least since 1980's. There are two approaches:

- build a brand new domain specific language such as Terraform. Those languages are called external.
- or an embedded domain specific language such as troposhere. Those languages are called internal.

Both approaches have pros & cons. The disadvantage of the first approach is the cost of building and learning a new language.
The disadvantage of the second one is the probably you can't have exactly the syntax or semantics that you want
and when coding you have to adhere to certain rules that cannot be statically verified during complication.

However, both approaches have some commonalities:

- syntax parsing
- build intermediate representation
- produce output/execute

## Summary

To summarize, to excel at *infrastructure as code* one needs to use a good programming language, appropriate code structuring practices and abstraction techniques.

# Building GraphFormation

In the next blog post we'll talk about how to take code snippets like this one and *execute* it.

```
mydir=directory(
  id="dir",
  location="/tmp/mydirectory"
)

file(
   id="contentfile",
   filename="file1",
   parent=ref(mydir),
   text="Lorem ipsum dolor"
)

file(
   id="downloadedfile",
   filename="file2",
   parent=ref(mydir),
   source="https://webserver.com/file.txt"
)
```

Essentially, we'd be building our own toy version of CloudFormation or Terraform.

To build Graphformation we'll proceed in stages.
- Write a sample program such as the one above
- Reference the driver that will validate the program and execute it
- The driver will produce an intermediate representation
- The executor will execute the intermediate representation

## Driver reference
```
from graphformation import *

mydir=directory(
...
)

file(
...
)

file(
...
)

dump_graph()
```

## Intermediate Representation

`dump_graph()` outputs the intermediate representation:

```
{
  "dir": {
    "properties": {
      "permissions": "700",
      "location": "/tmp/mydirectory"
    },
    "id": "dir",
    "type": "directory"
  },
  "contentfile": {
    "properties": {
      "filename": "file1",
      "text": "Lorem ipsum dolor",
      "permissions": "600",
      "parent": {
        "ref": "dir"
      }
    },
    "id": "contentfile",
    "type": "file"
  },
  "downloadedfile": {
    "properties": {
      "filename": "file2",
      "source": "https://webserver.com/file.txt",
      "parent": {
        "ref": "dir"
      },
      "permissions": "600"
    },
    "id": "downloadedfile",
    "type": "file"
  }
}
```

## Execution

```
from graphformation import *

mydir=directory(
...
)

file(
...
)

file(
...
)

execute()
```

The output is a bash program.

```
# create directory dir
mkdir -f /tmp/mydirectory 
# end


# create file contentfile
echo << ENDOFFILE
Lorem ipsum dolor
ENDOFFILE > /tmp/mydirectory/file1
 
# end


# create file downloadedfile
wget https://webserver.com/file.txt /tmp/mydirectory/file2 
# end
```

For more details stay tuned for the actual blog post. In the meantime you can refer to the [source code](https://github.com/stefansavev/graphformation/tree/master/demo/graphformation)

I believe going through this exercise is beneficial to learn how tools and CloudFormation and Terraform do their job.


# Code structuring in troposhere

As mentioned, [troposhere](https://github.com/cloudtools/troposphere) is a library that helps you generated CloudFormation templates. The benefits of using it is code structuring and abstraction. 

I am planning another blog post where I will talk about how to structure your infrastructure code in troposhere. The goal is code reuse and abstractions as used in software development. 

# Create a library in Java that generates CloudFormation

It is little known, but CloudFormation provides what is called [CloudFormation Resource Specification](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html). These are JSON files, one per region, that fully describe the CloudFormation Resources. I believe that one can take this specification and automatically generate the equivalent of troposhere in any language.
In this next blog post, I will take a crack at this problem. This is useful for example for Java developers as well as others who want to use a specific programming language. I also believe it will lead to a productivity boost if the library is designed with intellisense in mind.

As far as I know, both [troposhere](https://github.com/cloudtools/troposphere) and [GoFormation](https://github.com/awslabs/goformation) are hand-generated, so the code generation approach is an interesting to try.
