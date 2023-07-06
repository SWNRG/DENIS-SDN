# DENIS-SDN Dashboard
DENIS-SDN: Software-Defined Network Slicing Solution for Dense and Ultra-Dense IoT Networks

DENIS-SDN Dashboard, a user-friendly graphical interface operating at the SDN Application Layer. This
dashboard is equipped with a comprehensive range of network monitoring tools and mechanisms.

![DENIS-SDN Dashboard](../images/theod03-Dashboard.png)

__Slice Configurator__ allows the network administrator to
input configuration data for making network slicing decisions. This includes specifying the slice assignment for
each node within the network. To enhance usability, nodes
that have not been explicitly assigned to any slice by the
administrator are automatically included in the default
slice, simplifying the configuration process.

__Real-time Slice Manager__ allows the administrator to
manage network slices in real-time and dynamically make
instant adjustments to the slice configuration. To achieve
that NDC is utilizing the DENIS-SDN sub-GHz out-of-band control channel that can communicate and configure
the radio frequency of any of the network nodes in the range of the border router.

__Node Density Classifier__ is a real-time mechanism that
categorizes network nodes based on their adjacency information using a traffic light RAG rating coloring scheme.
It provides valuable insights for network management and
optimization, with red nodes indicating high-adjacency
load, amber and yellow nodes indicating medium load,
and green nodes indicating low adjacency load. The
classification is percentage-based rather than fixed numbers, allowing adaptability to different density conditions
and drawing attention to nodes requiring administrative
attention.

__Network Density Visualizer__ is a real-time graphical tool
that visually represents the network connectivity graph,
highlighting regions with high node density. It enables
administrators to quickly identify areas of concentrated
nodes, aiding in network analysis, capacity planning, and
identifying potential congestion points.
